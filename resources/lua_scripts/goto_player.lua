local player_list = game.Players:GetPlayers()
for i=1,#player_list do
    local current_player = player_list[i]
    if (string.lower(current_player.Name) == "{target}") then
        game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[Teleporting to player '" .. current_player.Name .."'!]" , "All")
        wait(10)
        local original_pos = game.Players.LocalPlayer.Character.PrimaryPart.Position
        local player_pos = current_player.Character.PrimaryPart.Position
        game.Players.LocalPlayer.Character:MoveTo(player_pos)
        wait(2)
        local current_pos = game.Players.LocalPlayer.Character.PrimaryPart.Position
        if (current_pos.y > 65) then
            game.Players.LocalPlayer.Character:MoveTo(original_pos)
            game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[This player is in a location I can't teleport to!]" , "All")
            game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[Can only teleport to players outside and not on objects!]" , "All")
            break
        else
            game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[Hello! Someone on T witch asked me to teleport to you.]" , "All")
        end
        break
    end
end
workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")