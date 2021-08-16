local player_list = game.Players:GetPlayers()
for i=1,#player_list do
    local current_player = player_list[i]
    if (string.lower(current_player.Name) == "{target}") then
        pcall(function()
            print(current_player.Name)
            print(current_player.Character:FindFirstChildOfClass("Humanoid"))
            workspace.CurrentCamera.CameraSubject = current_player.Character:FindFirstChildOfClass("Humanoid")
        end)
        break
    end
end