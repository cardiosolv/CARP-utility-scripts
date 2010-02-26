function shape = igb_size(filename)

header = igb_header(filename);

x = 0;
t = 0;

% parse the header to get the dimensions.
while (header)
    [tok, header] = strtok(header);
    [name,tok] = strtok(tok, ':');
    value = strtok(tok, ':');
    value = value';
    
    if (strcmp(name,'x'))
        x = str2num(value);
    end
    if (strcmp(name,'t'))
        t = str2num(value);
    end
end

shape = [x t];


function header = igb_header(filename)

fid = fopen(filename, 'r');
header = fread(fid, 1024, 'uint8=>char');
fclose(fid);
