print("\\n\\n")
print("Position:", game.Players.LocalPlayer.Character.PrimaryPart.Position)
print("Angles:", game.Players.LocalPlayer.Character.PrimaryPart.Rotation)
local campos = workspace.CurrentCamera.CFrame.Position
print("Camera Pos:", campos)
local camx, camy, camz = (workspace.CurrentCamera.CFrame - campos):ToEulerAnglesYXZ()
camx = math.floor(math.deg(camx)*10000)/10000
camy = math.floor(math.deg(camy)*10000)/10000
camz = math.floor(math.deg(camz)*10000)/10000
print("Camera Angles:", camx, camy, camz)
