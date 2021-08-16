local player_list = game.Players:GetPlayers()
for i=1,#player_list do
    local current_player = player_list[i]
    if (string.lower(current_player.Name) == "{target}") then
        local original_pos = game.Players.LocalPlayer.Character.PrimaryPart.Position
        local player_pos = current_player.Character.PrimaryPart.Position
        game.Players.LocalPlayer.Character:SetPrimaryPartCFrame(CFrame.new(player_pos), game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame.LookVector)


        break
    end
end
workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")