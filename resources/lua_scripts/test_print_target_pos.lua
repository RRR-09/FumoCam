local player_list = game.Players:GetPlayers()
for i=1,#player_list do
    local current_player = player_list[i]
    if (string.lower(current_player.Name) == "{target}") then
        local original_pos = game.Players.LocalPlayer.Character.PrimaryPart.Position
        local player_pos = current_player.Character.PrimaryPart.Position
        print("Target:", current_player.Name)
        print("\\n\\n")
        print("Position:", current_player.Character.PrimaryPart.Position)
        print("Angles:",  current_player.PrimaryPart.Rotation)

        break
    end
end
workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")