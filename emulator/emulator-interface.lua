require "io"

function getos()

        -- Unix, Linux varients
        fh,err = io.popen("uname -o 2>/dev/null","r")
        if fh then
                osname = fh:read()
                end
        if osname then return osname end

        -- Add code for other operating systems here
        return "unknown"
end

os = getos()
if os=="unknown" then
    -- Windows
    data_path = '\\\\.\\pipe\\mariofifo-data'
    command_path = '\\\\.\\pipe\\mariofifo-command'

    --dataFifo = assert(io.open(data_path,"wb"))
    commandFifo = assert(io.open(command_path, "rb"))
else
    -- Linux
    dataFifo = assert(io.open("/tmp/mariofifo-data", "wb"))
    dataFifo2 = assert(io.open("/tmp/mariofifo-data2", "wb"))
    commandFifo = assert(io.open("/tmp/mariofifo-command", "rb"))
end

emu.speedmode("maximum");
emu.softreset()
emu.frameadvance()

while (true) do
    local screenshot = gui.gdscreenshot();
    local xpos = memory.readbyterange(0x03AD, 1);
    local enemyPos1 = memory.readbyterange(0x03AE, 1);
    local enemyPos2 = memory.readbyterange(0x03AF, 1);
    local enemyPos3 = memory.readbyterange(0x03B0, 1);
    local enemyPos4 = memory.readbyterange(0x03B1, 1);
    local enemyPos5 = memory.readbyterange(0x03B2, 1);
    local playerAbsPos = memory.readbyterange(0x071C, 1);
    local level = memory.readbyterange(0x07A0, 1);
    local xSpeed = memory.readbyterange(0x0057, 1);
    local airborne = memory.readbyterange(0x001D, 1);
    local timerC = memory.readbyterange(0x07F8, 1);
    local timerD = memory.readbyterange(0x07F9, 1);
    local timerU = memory.readbyterange(0x07FA, 1);
    local state = memory.readbyterange(0x000E, 1);
    local currentScreen = memory.readbyterange(0x071A, 1);

    dataFifo2:write(xpos .. enemyPos1 .. enemyPos2 .. enemyPos3 .. enemyPos4 .. enemyPos5 .. playerAbsPos .. level .. xSpeed .. airborne .. timerC .. timerD .. timerU .. state ..currentScreen);
    dataFifo2:flush();
    dataFifo:write(screenshot);
    dataFifo:flush();

    command = commandFifo:read(1)
    command = string.byte(command,1)

    input = {};
--       print(string.format("%i", string.byte(command,1)))

    if AND(command, 1) == 1 then
        input.up = true;
    else
        input.up = false;
    end
    if AND(command, 2) == 2 then
        input.down = true;
    else
        input.down = false;
    end
    if AND(command, 4) == 4 then
        input.left = true;
    else
        input.left = false;
    end
    if AND(command, 8) == 8 then
        input.right = true;
    else
        input.right = false;
    end
    if AND(command, 16) == 16 then
        input.A = true;
    else
        input.A = false;
    end
    if AND(command, 32) == 32 then
        input.B = true;
    else
        input.B = false;
    end
    if AND(command, 64) == 64 then
        input.start = true;
    else
        input.start = false;
    end
    if AND(command, 128) == 128 then
        input.select = true;
    else
        input.select = false;
    end

    if command == 255 then
--         print("reset")
        emu.softreset()
    else
--         print(input);
        joypad.set(1, input);
    end
    emu.frameadvance();
end;
