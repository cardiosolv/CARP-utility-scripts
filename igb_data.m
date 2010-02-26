function data = igb_data(filename, node, time)
% Returns the data from an IGB file
% Warning!  Uses 0 based indexing!  To get the results from node 0, put in 
% 0 into this file.  Returns Matlab arrays.  Be careful!
%
% Node or time can be an integer, or one or both can be 'all'.  Specifying 
% 'all' is like using : in a matlab array.

shape = igb_size(filename);
fid = fopen(filename, 'r');
fseek(fid, 1024, 'bof');

if strcmp(node, 'all') && strcmp(time, 'all')
    data = fread(fid, shape, 'float32=>double');
elseif strcmp(node, 'all') && isnumeric(time)
    fseek(fid, shape(1)*time*4, 'cof');
    data = fread(fid, shape(1), 'float32=>double');
elseif strcmp(time, 'all') && isnumeric(node)
    fseek(fid, node*4, 'cof');
    data = fread(fid, shape(2), 'float32=>double', 4*shape(1));
else
    fseek(fid, (shape(1)*time+node)*4, 'cof');
    data = fread(fid, 1, 'float32=>double');
end

fclose(fid);