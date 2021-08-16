-- The factor by which gravity will be counteracted
local MOON_GRAVITY = {desired_gravity}
local function setGravity(part, g)
    local antiGravity = part:FindFirstChild("AntiGravity")
    if g == 1 then
        -- Standard gravity; destroy any gravity-changing force
        if antiGravity then
            antiGravity:Destroy()
        end
    else
        -- Non-standard gravity: create and change gravity-changing force
        if not antiGravity then
            antiGravity = Instance.new("BodyForce")
            antiGravity.Name = "AntiGravity"
            antiGravity.Archivable = false
            antiGravity.Parent = part
        end
        antiGravity.Force = Vector3.new(0, part:GetMass() * workspace.Gravity * (1 - g), 0)
    end
end
local function moonGravity(part)
    setGravity(part, MOON_GRAVITY)
end
local function recursiveMoonGravity(object)
    if object:IsA("BasePart") then
        moonGravity(object)
    end
    for _, child in pairs(object:GetChildren()) do
        recursiveMoonGravity(child)
    end
end
local function onDescendantAdded(object)
    if object:IsA("BasePart") then
        moonGravity(object)
    end
end
recursiveMoonGravity(workspace)
workspace.DescendantAdded:Connect(onDescendantAdded)