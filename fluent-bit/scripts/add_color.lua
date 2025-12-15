function add_color(tag, timestamp, record)
    -- Map app names to their colors
    local color_map = {
        ["APP1"] = "#007bff",  -- blue
        ["APP2"] = "#28a745",  -- green
        ["APP3"] = "#fd7e14"   -- orange
    }
    
    local app_name = record["appname"]
    
    -- Add color based on app name
    if app_name and color_map[app_name] then
        record["color"] = color_map[app_name]
    else
        record["color"] = "#6c757d"  -- default gray
    end
    
    -- Return the modified record
    return 1, timestamp, record
end