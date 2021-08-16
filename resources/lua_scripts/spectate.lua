local function shuffle(array)
    -- fisher-yates
    local output = { }
    local random = math.random
    for index = 1, #array do
        local offset = index - 1
        local value = array[index]
        local randomIndex = offset*random()
        local flooredIndex = randomIndex - randomIndex%1
        if flooredIndex == offset then
            output[#output + 1] = value
        else
            output[#output + 1] = output[flooredIndex + 1]
            output[flooredIndex + 1] = value
        end
    end
    return output
end
local player_list = game.Players:GetPlayers()
player_list = shuffle(player_list)
for i=1,math.min(#player_list,10) do
    pcall(function()
        local current_player = player_list[i]
        print(current_player.Name)
        print(current_player.Character:FindFirstChildOfClass("Humanoid"))
        workspace.CurrentCamera.CameraSubject = current_player.Character:FindFirstChildOfClass("Humanoid")
        wait(5)
    end)
end
workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")