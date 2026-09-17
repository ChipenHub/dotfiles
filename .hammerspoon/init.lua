local mouseEvents = hs.eventtap.event.types

-- Clamp the original movement event, not the live cursor: warping the cursor
-- repeatedly interrupts motion along the edge and can interfere with clicks.
-- Keep a global reference so the event tap is not garbage-collected.
leftEdgeMouseTap = hs.eventtap.new({
    mouseEvents.mouseMoved,
    mouseEvents.leftMouseDragged,
    mouseEvents.rightMouseDragged,
    mouseEvents.otherMouseDragged,
}, function(event)
    if event:getFlags().cmd then
        return false
    end

    local point = event:location()
    for _, screen in ipairs(hs.screen.allScreens()) do
        local frame = screen:fullFrame()
        if point.x >= frame.x and point.x < frame.x + 1
            and point.y >= frame.y and point.y < frame.y + frame.h then
            point.x = frame.x + 1
            event:location(point)
            break
        end
    end
    return false
end):start()
