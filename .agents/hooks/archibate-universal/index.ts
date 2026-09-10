import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { spawn } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HOOK_DIR = dirname(fileURLToPath(import.meta.url));
const HOOK_TIMEOUT_MS = 5_000;

type HookSpecificOutput = {
	permissionDecision?: "deny";
	permissionDecisionReason?: string;
	additionalContext?: string;
};

type HookEvent = {
	session_id: string;
	tool_name: "Bash" | "Edit" | "Write";
	tool_input: Record<string, unknown>;
};

function runHook(
	scriptName: string,
	event: HookEvent,
	cwd: string,
	signal?: AbortSignal,
): Promise<HookSpecificOutput | undefined> {
	return new Promise((resolve, reject) => {
		const child = spawn(join(HOOK_DIR, scriptName), [], {
			cwd,
			env: process.env,
			stdio: ["pipe", "pipe", "pipe"],
		});
		let stdout = "";
		let stderr = "";
		let timedOut = false;
		let settled = false;

		const cleanup = () => {
			clearTimeout(timeout);
			signal?.removeEventListener("abort", onAbort);
		};
		const fail = (error: Error) => {
			if (settled) return;
			settled = true;
			cleanup();
			reject(error);
		};
		const onAbort = () => child.kill();
		const timeout = setTimeout(() => {
			timedOut = true;
			child.kill();
		}, HOOK_TIMEOUT_MS);

		signal?.addEventListener("abort", onAbort, { once: true });
		if (signal?.aborted) onAbort();

		child.stdin.on("error", (error) => fail(error));
		child.stdout.setEncoding("utf8");
		child.stderr.setEncoding("utf8");
		child.stdout.on("data", (chunk: string) => {
			stdout += chunk;
		});
		child.stderr.on("data", (chunk: string) => {
			stderr += chunk;
		});
		child.on("error", (error) => fail(error));
		child.on("close", (code) => {
			if (settled) return;
			settled = true;
			cleanup();

			if (timedOut) {
				reject(new Error(`${scriptName} timed out after ${HOOK_TIMEOUT_MS}ms`));
				return;
			}
			if (signal?.aborted) {
				reject(new Error(`${scriptName} was aborted`));
				return;
			}
			if (code !== 0) {
				reject(new Error(`${scriptName} exited with code ${code}: ${stderr.trim()}`));
				return;
			}

			const output = stdout.trim();
			if (!output) {
				resolve(undefined);
				return;
			}
			try {
				const parsed = JSON.parse(output) as { hookSpecificOutput?: HookSpecificOutput };
				resolve(parsed.hookSpecificOutput);
			} catch {
				reject(new Error(`${scriptName} returned invalid JSON: ${output}`));
			}
		});

		child.stdin.end(JSON.stringify(event));
	});
}

function toHookEvent(
	toolName: string,
	input: Record<string, unknown>,
	sessionId: string,
): HookEvent | undefined {
	if (toolName === "bash" && typeof input.command === "string") {
		return { session_id: sessionId, tool_name: "Bash", tool_input: { command: input.command } };
	}
	if (toolName === "edit" && typeof input.path === "string") {
		return { session_id: sessionId, tool_name: "Edit", tool_input: { file_path: input.path } };
	}
	if (toolName === "write" && typeof input.path === "string") {
		return { session_id: sessionId, tool_name: "Write", tool_input: { file_path: input.path } };
	}
	return undefined;
}

export default function (pi: ExtensionAPI) {
	const pendingContext = new Map<string, string>();

	pi.on("tool_call", async (event, ctx) => {
		if (event.toolName !== "bash") return undefined;

		const hookEvent = toHookEvent(event.toolName, event.input, ctx.sessionManager.getSessionId());
		if (!hookEvent) return undefined;

		try {
			const output = await runHook("block_risky_bash.py", hookEvent, ctx.cwd, ctx.signal);
			if (output?.permissionDecision === "deny") {
				return {
					block: true,
					reason: output.permissionDecisionReason ?? "Blocked by the Archibate Bash guard",
				};
			}
			if (output?.additionalContext) {
				// tool_call cannot inject context, so attach the advisory to this call's result.
				pendingContext.set(event.toolCallId, output.additionalContext);
			}
			return undefined;
		} catch (error) {
			return {
				block: true,
				reason: `Archibate Bash guard failed: ${error instanceof Error ? error.message : String(error)}`,
			};
		}
	});

	pi.on("tool_result", async (event, ctx) => {
		const contexts: string[] = [];
		const preToolContext = pendingContext.get(event.toolCallId);
		pendingContext.delete(event.toolCallId);
		if (preToolContext) contexts.push(preToolContext);

		const hookEvent = toHookEvent(event.toolName, event.input, ctx.sessionManager.getSessionId());
		const scriptName =
			event.toolName === "bash"
				? "remind_uv_python.py"
				: !event.isError && (event.toolName === "edit" || event.toolName === "write")
					? "post_edit_self_review.py"
					: undefined;

		if (hookEvent && scriptName) {
			try {
				const output = await runHook(scriptName, hookEvent, ctx.cwd, ctx.signal);
				if (output?.additionalContext) contexts.push(output.additionalContext);
			} catch (error) {
				if (ctx.hasUI) {
					ctx.ui.notify(
						`Archibate hook failed: ${error instanceof Error ? error.message : String(error)}`,
						"warning",
					);
				}
			}
		}

		if (contexts.length === 0) return undefined;
		return {
			content: [
				...event.content,
				{ type: "text" as const, text: `[Archibate hook context]\n${contexts.join("\n\n")}` },
			],
		};
	});
}
