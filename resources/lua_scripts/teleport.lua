game.Players.LocalPlayer.Character:SetPrimaryPartCFrame(CFrame.new(Vector3.new({pos}), game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame.LookVector))
game.Players.LocalPlayer.Character.PrimaryPart.CFrame = CFrame.new(game.Players.LocalPlayer.Character.PrimaryPart.Position) * CFrame.Angles({rot})
workspace.CurrentCamera.CFrame = CFrame.new(workspace.CurrentCamera.CFrame.Position) * CFrame.Angles({cam_rot})