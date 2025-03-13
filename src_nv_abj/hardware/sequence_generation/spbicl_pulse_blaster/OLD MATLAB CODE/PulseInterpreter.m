%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%PulseInterpreter class
%Author: Eric Miller
%Date of last edit: 9/15
%Questions: e-mail ejm01@umail.ucsb.edu
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
    %In order to communicate with the pulseblaster, I had to make my own
    %format for Matlab to follow. Thus, programs are saved as an Nx5
    %matrix, where each column has the following meaning:
    %
        %Column 1: The line number for the code. The pulse blaster starts
        %at 0, so I mimicked this. This is just to make sure that the
        %pulseblaster and the user's code are in agreement.
        %
        %Column 2: The value sent to the pulseblaster indicating which bits
        %to turn on, in decimal. The pulseblaster refuses to keep any bits
        %on for longer than 5 clock cycles unless the last 3 bits (hex E00000)
        %are on, hence the large numbers.
        %
        %Column 3: The code corresponding to the desired command. These are
        %listed in the user manual for the Pulseblaster on page 21.
        %
        %Column 4: This is data specific to the instruction. Information on
        %this can be found in the user manual for the Pulseblaster on page
        %21.
        %
        %Column 5: The number of clockcycles per command. As far as I can tell, the
        %pulseblaster waits this long after issuing every command, so this 
        %is ignored for stop and wait commands.
        

classdef PulseInterpreter < handle
    
    properties
        currentInstruction = [];
        %The currentInstruction property lists a set of commands that will
        %be used by default. The only class command that changes this is
        %the setCurrentPulse function.
    end
    
    properties(Constant)
        % property of the SpinCore ESR PRO 500 pulse blaster board 
        CLOCKSPEED = 500;
        SPINAPI_DLL_PATH = 'C:\SpinCore\SpinAPI\lib\';
        SPINAPI_DLL_NAME = 'spinapi64';

    end
    
    methods
        
        function obj = PulseInterpreter()
            %Simple constructor loading the library if it hasn't been loaded.
            if libisloaded(obj.SPINAPI_DLL_NAME) ~= 1
                loadlibrary(strcat(obj.SPINAPI_DLL_PATH, obj.SPINAPI_DLL_NAME, '.dll'), 'C:\SpinCore\SpinAPI\include\spinapi.h', 'addheader','C:\SpinCore\SpinAPI\include\pulseblaster.h');
            end
             
        end
        
        function setCurrentPulse(obj, varargin)
        %Sets the currentInstruction property. If input is an Nx5 numeric
        %matrix, currentInstruction is set to that input. If input if a
        %filename, that file is loaded and used to set the
        %currentInstruction preperty. If no inputs are given, the user will
        %be prompted with a uigetfile box to select a file from.
        %
        %If the user passes more than one argument, all but the first are
        %ignored.
        
            if nargin == 2
                if isnumeric(varargin{1})
                    if size(varargin{1}, 2) == 5
                        obj.currentInstruction = varargin{1};
                    end
                else
                    obj.currentInstruction = obj.loadPulse(varargin{1});
                end
            else
                obj.currentInstruction = obj.loadPulse();
            end
        end
        
        function savePulse(obj, varargin)
        %Saves currentInstruction to a text file. savePulse can take up to
        %two inputs. 
        %
        %If the user inputs just an Nx5 array, he will be
        %prompted with the standard file-save dialog box for a filename to
        %save to. 
        %
        %If just the filename is specified, the currentInstruction property
        %is saved to that file.
        %
        %If both are specified (in any order), the matrix is saved to the
        %file specified.
        
            %if no arguments are passed, prompt the user for a file
            %location and then proceed as if it had been passed.
            if nargin == 1
                [filename pathname] = uiputfile('*.txt', 'Select file to save to', ...
                    'C:\Users\LT-SPM\Documents\MATLAB\PulseBlaster\PulseSequences\');
                varargin{1} = [pathname filename];
            end
            
            %If the first input is a filename
            if ischar(varargin{1})
                fid = fopen(varargin{1}, 'wt');
                if fid == -1
                    error('Input to savePulse must either be empty or a real filename (with path optional)')
                end
                
                %check to see if an Nx5 matrix was also passed, and if so,
                %save that to the file instead of obj.currentInstruction.
                %Otherwise, save obj.currentInstruction;
                if nargin >= 3
                    if isnumeric(varargin{2})
                        if size(varargin{2},2)==5
                            fprintf(fid, '%i\t%i\t%i\t%i\t%.3f\n', varargin{2}');
                        else
                            fclose(fid);
                            return;
                        end
                    else
                        fprintf(fid, '%i\t%i\t%i\t%i\t%.3f\n', obj.currentInstruction');
                    end
                else
                    fprintf(fid, '%i\t%i\t%i\t%i\t%.3f\n', obj.currentInstruction');
                end
                fclose(fid);
            end
            
            %The case where the first input is an Nx5 matrix. This does
            %exactly what the previous block did, but with the arguments in
            %the other order.
            if isnumeric(varargin{1})
                if nargin == 2
                    [filename pathname] = uiputfile('*.txt', 'Select file to save to', ...
                        'C:\Users\lab\Documents\code\MATLAB\NewPulseBlaster\SavedPulseSequences\');
                    varargin{2} = [pathname filename];
                end
                try
                    fid = fopen(varargin{2}, 'wt');
                catch err %#ok
                    return;
                end
                if fid == -1
                    error('Input to savePulse must either be empty or a real filename (with path optional)')
                end
                if size(varargin{1}, 2)==5
                    fprintf(fid, '%i\t%i\t%i\t%i\t%.3f\n', varargin{1}');
                end
                fclose(fid);
            end
        end
        
        function loadToPulseblaster(obj, varargin)
            %Loads the currentInstruction to the pulseblaster. Will return
            %an error if the spinapi library was not loaded properly or if
            %the pulseblaster is not installed.
            if nargin == 2
                if isnumeric(varargin{1}) && ~isempty(varargin{1})&&size(varargin{1}, 2)==5
                    obj.setCurrentPulse(varargin{1});
                end
            end
            if isempty(obj.currentInstruction)
                return;
            end %No instructions, nothing to do
            
            %Convert ns to clockcycles
            output = obj.currentInstruction;
            %Initialize the pulseblaster if it is not already initialized
            if ~any([1 2 4 8] == pb_read_status)
                    %pb_read_status returns a 1,2,4, or 8, depending on the
                    %status of the pulseblaster. If the pulseblaster is not
                    %initialized, it returns 0 or a negative integer.
                    
                err = pb_init();
                
                if err < 0 %Pulseblaster always returns neg on error
                    error('Pulseblaster did not initialize correctly');
                end
                pb_core_clock(obj.CLOCKSPEED); %sets the clock speed in MHz. This is the speed of our pulseblaster.
            end
            err = pb_start_programming('PULSE_PROGRAM');
            if err < 0
                error('Pulseblaster did not initialize correctly');
            end
            %Pass all the commands to the pulseblaster.
            for i = 1:size(output, 1)
                num_flag = dec2hex(output(i,2));
                %I think it makes more sense to pass in hex values for
                %which bits to turn on, but it will accept decimal values
                %also.
                
                %This just makes all the input values be 6 characters long
                %by adding 0's to the front. Once again, not necessary, but
                %makes more sense to me.
                if length(num_flag)<6
                    for j = 1:(6-length(num_flag))
                        num_flag = ['0' num_flag]; %#ok<AGROW>
                    end
                end
                
                op_code = output(i,3);
                inst_data = output(i,4);
                time_len = 2*floor(.5*output(i,5));
                out_code = pb_inst_pbonly(num_flag, op_code, inst_data, time_len);
                
                %The out_code value is the line number for the code that
                %the pulseblaster just received. If it is different from
                %what Matlab has (stored as the first column in the
                %currentInstruction property), it should return an error
                %so that the user checks his program to make sure it is
                %right.
                if out_code ~= output(i, 1)
                    error(sprintf(['There was a problem loading the program into the pulseblaster.'...
                        'Either the loaded program has an error, or\n'...
                        '\tMatlab''s instructions do not line up with those passed to the Pulseblaster.\n'...
                        '\tMake sure that your code is properly formatted then try again.'])); %#ok<SPERR>
                end
            end
            pb_stop_programming();
        end
        
        function finalInst = reconcilePulses(obj, varargin)
            %Combines multiple pulse sequences across the various channels
            %into one single program. The pulseblaster cannot run two bits
            %independently, but this is often the desired behavior. This
            %program replicates this desired behavior by combining the
            %desired program for each channel into a single program
            %operating all of them.
            %
            %Takes up to 21 pulse sequences as its argument.
            
            %If no arguments are passed, return the currentInstruction
            if nargin == 1
                finalInst = obj.currentInstruction;
                return
            end
            
            %If two pulse sequences use the same port, they could conflict
            %with each other. To avoid this, throw an error if the user
            %tries to combine two sequences that both use the same bit
         %   ports = obj.findOpenPorts(varargin);
         %   if size(ports.Used, 1) > 1
         %       if max(sum(ports.Used))>1
         %           error(['Ports ' sprintf('%i, ', find(sum(ports.Used)>1))...
         %               'are in conflict. No two pulse sequences may use the same port.']);
         %       end
         %   end
            
            %First, decompress the pulse sequence for each bit separately.
            %More on this in the decompressPulse function.
            
           % varargin{:}
           
           %This code removes any lines with 0 duration, since the pulse
           %blaser may not behave well with commands of 0 length
            [s1 s2] = size(varargin);
            for i = 1:s2
                [q1 q2] = size(varargin{i});
                sum(varargin{i}(:,5));
                
                j = 1;
                while (j <= q1)
                    if varargin{i}(j,5) == 0
                        for k = (j+1):q1
                            varargin{i}(k,1) = varargin{i}(k,1) - 1;
                        end
                        
                        varargin{i}(j,:) = [];
                        j = 0;
                        [q1 q2] = size(varargin{i});

                    end
                    j = j+1;
                    
                end
            end
            
            varargin{:};
           
            [pulses, bStop, lineWait] = obj.decompressPulse(varargin{:});
            
            %pulses{1,:}
            %Combine the sequences for each bit together into one large
            %program controlling all of them. More on this in the
            %combinePulses function;
            endPulse = obj.combinePulses(pulses, lineWait);
            
            %Finally, compress the pulse down into the format used by
            %currentInstruction and return the result;
            finalInst = obj.compressPulse(endPulse);
            if bStop
                finalInst(end, 3) = 1;
            end
        end
        
        function [out] = findOpenPorts(obj, varargin)
            %Finds out which bits are being used by which pulse sequence,
            %and returns them in a struct. The out.Used array is a list of
            %which bits each sequence uses, and the out.Open vector is a
            %list of which bits are not used by any program;
            
            %If no input arguments are passed, use obj.currentInstruction.
            %If that is empty, then all ports are open.
            if nargin == 1
                if isempty(obj.currentInstruction)
                    out.Used = zeros(1,21);
                    out.Open = ones(1,21);
                    return
                end
                varargin{1} = obj.currentInstruction;
            end
            
            %Passing one function's varargin directly to another function as
            %varargin results in a cell of cells. Because this function is
            %passed the varargin of reconcile pulses, it needs to be able
            %to expand this into what we expect as varargin: a cell vector.
            if nargin == 2
                if iscell(varargin{1})
                    t = varargin{1};
                    for j = 1:length(t)
                        varargin{j} = t{j};
                    end
                end
            end
            
            len = length(varargin); %number of input arguments
            out.Used = zeros(len, 21);%initialize the out.Used array
            
            %For each input argument, check which ports are being used and
            %return them as a vector. cellfun called with 'UniformOutput'
            %set to false always returns an array of cells, in this case a
            %vector, so we have to convert these into a single matrix as
            %out.Used
            outcell = cellfun(@checkPorts, varargin, 'UniformOutput', false);
            for i = 1:len
                out.Used(i, :) = outcell{i};
            end
            
            %The checkPorts function
            function outp = checkPorts(incell)
                %Takes a single cell or matrix input and determines which
                %bits (0-3) it is using.
                
                if iscell(incell)
                    temp = incell{1};
                else
                    temp = incell;
                end
                
                %convert the data values for this specific pulse sequence
                %into binary so it is easy to determine which bits are in
                %use, then flip the numbers around so that it's easier to
                %deal with
                binvals = fliplr(dec2bin(temp(:,2)));
                
                if size(binvals, 2) < 21
                    outp = zeros(1, 21);
                    if size(binvals, 1) == 1
                        %if there is only one command listed, then just
                        %check each bit and output whether it is in use or
                        %not
                        outp(1:size(binvals, 2)) = arrayfun(@(inp)strcmp(inp, '1'), binvals);
                    else
                        %if there are multiple commands, then return a 1
                        %for each bit if it is used anywhere in the pulse
                        %sequence
                        outp(1:size(binvals, 2)) = any(arrayfun(@(inp)strcmp(inp, '1'), binvals));
                    end
                else
                    if size(binvals, 1) == 1
                        %if there is only one command listed, then just
                        %check each bit and output whether it is in use or
                        %not
                        outp = arrayfun(@(inp)strcmp(inp, '1'), binvals(1:21));
                    else
                        %if there are multiple commands, then return a 1
                        %for each bit if it is used anywhere in the pulse
                        %sequence
                        outp = any(arrayfun(@(inp)strcmp(inp, '1'), binvals(:, 1:21)));
                    end
                end
            end %end checkPorts
            
            %define out.Open to return a 1 if no pulse sequence uses it
            if len == 1
                out.Open = ~out.Used;
            else
                out.Open = ~any(out.Used);
            end
        end
        
        function delete(obj)
            %Simple destructor. Clears the pulseblaster and closes it in
            %the case that the spinapi library was loaded properly.
            if libisloaded('spinapi')
                obj.clearPulseblaster();
            end
        end
    end
    
    methods(Static)
        
        function [pulses, bStop, lineWait] = decompressPulse(varargin)
            %This is where stuff gets nasty. This function decompresses
            %each pulse sequence passed to it and returns a 2x4 cell array
            %(can be made longer to accommodate more bits.
            %
            %Takes the out.Used/out.Open structure returned by the
            %findOpenPorts function and each pulse sequence as arguments.
            %
            %Returns a 2x4 cell array. The first row holds the decompressed
            %pulses, while the second row holds information about infinite
            %loops if one should appear. This program will not allow for
            %more than one bit to be trapped in an infinite loop.
            %
            %If you try to combine more than one program with infinite 
            %loops or have one program using more than one bit that starts
            %an infinite loop, an error will be thrown. To make pulse
            %sequences in which multiple bits are trapped in an infinite
            %loop, first write all programs without the infinite loop and
            %combine them, then append the infinite loop using the
            %appendPulses function.
            
            %Passing one function's varargin directly to another function as
            %varargin results in a cell of cells. Because this function is
            %passed the varargin of reconcile pulses, it needs to be able
            %to expand this into what we expect as varargin: a cell vector.
            if nargin == 2
                if iscell(varargin{1})
                    t = varargin{1};
                    for j = 1:length(t)
                        varargin{j} = t{j};
                    end
                end
            end
            if length(varargin) > 21
                error('It is not possible to combine more than 21 pulse sequences.');
            end

            pulses{2, length(varargin)} = []; %Initialize the output variable
            lineWait{1,length(varargin)} = [];%Initialize the other output var
            bMultInfLoop = false;   %boolean storing whether or not an infinite loop has been detected.
                                    %If more than one infinite loop has
                                    %been detected, returns an error at the
                                    %end.
            bStop = true;
            finalTime = 0;
            
            
            %decompress each bit by itself
            for k = 1:length(varargin)
                
                %if the (k-1)th bit is not used, simply set the
                %corresponding entries in the output to empty matrices and
                %continue with the next bit.
                try
                    currentPulse = varargin{1, k};
                catch err %#ok<NASGU>
                    pulses{1,k} = [];
                    pulses{2,k} = [];
                    continue;
                end
                
                
                %initialize variables
                currentLine = 0; %stores which line in the sequence is being decompressed
                time = 0; %initialize time to 0
                loops = []; %array holding information about the finite loops currently being processed
                infloop = false; %boolean storing whether this bit has had an infinite loop
                lastline = 0; %stores the previously-decompressed line
                rts = []; %stores information about sub-routines, similar to the loops array
                bStopTemp = false;
                
                [mx my] = size(varargin{1,k});
                lineWait{1,k} = zeros(1,mx);
                
                %Follows each command exactly as the pulseblaster would.
                %For every command given, information on the state of the
                %bit in question and how long has passed since the pulse
                %sequence started is stored in the pulses array.
                
                while infloop == false      %Stop in an infinite loop has been detected
                    
                    %stops if the program has run out of lines or if
                    %something causes it to try to acces a negative line
                    %(which can't exist)
                    if currentLine > max(currentPulse(:,1)) | currentLine < 0
                        pulses{1,k}(end+1,:) = [0 time]; %set the bit to off and list the time
                        break
                    end
                    
                    %command is just the current line being looked at
                    
                    command = currentPulse(currentPulse(:,1)==currentLine, :);
                    
                    %get whether the bit in question is on or off at this
                    %line, and store the current time
                    
                    if command(2)>hex2dec('E00000')
                        command(2) = command(2)-hex2dec('E00000');
                    end
                    if isempty(pulses{1,k})
                        pulses{1,k}(1,:) = [command(2) time];
                    else
                        pulses{1,k}(end+1, :) = [command(2) time];
                    end
                    
                    %Processes the next command given. Information on what
                    %each command number means is listed in the user manual
                    %for the pulseblaster on page 21.
                    switch command(3)
                        case 0 %CONTINUE
                            lastline = currentLine;
                            currentLine = currentLine + 1;
                            %goes on to next line
                            
                        case 1 %STOP
                            lastline = currentLine;
                            currentLine = -1;
                            bStopTemp = true;
                            %set the current line to -1, ending this pulse
                            %sequence
                            
                        case 2 %LOOP
                            if isempty(loops)
                                %if this is the first loop found, then set
                                %the variable 'loops.' The format for this
                                %is [(line# of start of loop), (number of
                                %times to loop), (number of times gone
                                %through loop so far)]
                                %
                                %looping one time through does nothing,
                                %looping twice is the same as repeating
                                %once, etc.
                                loops = [currentLine command(4) 1];
                            else
                                %if there are already loops, just add this
                                %one to the end of 'loops.' (The order
                                %of the variable 'loops' doesn't actually
                                %matter)
                                if currentPulse(currentPulse(:,1)==lastline, 3) ~= 3
                                    loops(end+1, :) = [currentLine command(4) 1]; %#ok<AGROW>
                                end
                            end
                            lastline = currentLine;
                            currentLine = currentLine + 1;
                            %Then go on to next line
                            
                        case 3 %END_LOOP
                            %If this is the end of a loop, then find the
                            %loop info for the start of the loop. If
                            %something went wrong and the corresponding
                            %loop wasn't started, then just continue
                            %instead.
                            if any(loops(:,1) == command(4))
                                ind = find(loops(:,1) == command(4));
                            else
                                lastline = currentLine;
                                currentLine = currentLine + 1;
                                continue;
                            end
                            
                            %If the loop has gone through the correct
                            %number of times, then just continue.
                            %Otherwise, note (in the last column of 'loops'
                            %that the loop has gone through another
                            %repetition, then go back to the start
                            if loops(ind, 3) == loops(ind, 2)
                                lastline = currentLine;
                                currentLine = currentLine + 1;
                                loops(ind, :) = []; %#ok<AGROW>
                                %clear this loop from memory, then go on
                            else
                                lastline = currentLine;
                                currentLine = command(4);
                                loops(ind, 3) = loops(ind, 3)+1; %#ok<AGROW>
                                %store that we've gone through one more
                                %time, then start again
                            end
                            
                        case 4 %JSR
                            %jumps to sub-routine, storing the line to
                            %return to after execution of the subroutine in
                            %the rts vector
                            if isempty(rts)
                                rts(1) = currentLine+1;
                            else
                                rts(end+1) = currentLine+1; %#ok<AGROW>
                            end
                            lastline = currentLine;
                            currentLine = command(4); %jump to sub-routine
                            
                        case 5 %RTS
                            %returns back to the line after the one that
                            %sent the program to the sub-routine
                            lastline = currentLine;
                            if isempty(rts)
                                %if this sub-routine wasn't jumped to, then
                                %just continue
                                currentLine = currentLine + 1;
                            else
                                currentLine = rts(end); %go back to main routine
                                rts(end) = []; %#ok<AGROW>
                            end
                            
                        case 6 %BRANCH
                            %Jumps to the line listed in the instruction
                            %data for this command. Can create infinite
                            %loops, so this needs to be watched out for.
                            lastline = currentLine;
                            
                            %If the BRANCH command takes the code back to a
                            %previous line, it will automatically be
                            %assumed to create an infinite loop regardless
                            %of whether or not it actually does.
                            if ~isempty(pulses{2,k})&&command(4)<=currentLine
                                infloop = true; %an infinite loop has been detected
                                
                                if bMultInfLoop == true
                                    %if this isn't the first infinite loop,
                                    %throw an error
                                    error(['It cannot be guaranteed that multiple infinite loops can run together. Try re-writing one'...
                                        ' or more' sprintf('\n') 'pulse sequences so that only one sequence is in an infinite loop.' sprintf('\n\n')...
                                        'This may be fixed in a later version.']);
                                else
                                    %if this is the first infinite loop
                                    %encountered, set this boolean to be
                                    %true to cause errors if any other bits
                                    %hit an infinite loop
                                    bMultInfLoop = true;
                                end
                                
                                %The next chunk of code is all about saving
                                %the required information for the infinite
                                %loop and setting up everything before the
                                %infinite loop so that it can be integrated
                                %properly into the final pulse sequence
                                
                                currentLine = command(4); %Jump to line specified by instruction data
                                time = time+command(5); %increment time
                                command = currentPulse(currentPulse(:,1)==currentLine, :); %find what the next line should be
                                %complete one more line to make sure that
                                %we have enough information to process the
                                %infinite loop
                                if command(2)>hex2dec('E00000')
                                    command(2) = command(2)-hex2dec('E00000');
                                end
                                pulses{1,k}(end+1, :) = [command(2), time];
                                endLine = pulses{2,k}(1); %last line before the loop started
                                pulses{1,k}(endLine, :) = pulses{2,k}(2:3); %reset the corresponding line of pulses{1,k}
                                pulses{2,k} = pulses{1,k}(endLine:end, :); %pulses{2,k} takes everything that was contained in the infinite loop
                                pulses{1,k}(endLine+2:end, :) = []; %pulses{1,k} is cleared of everything that is contained in the infinite loop
                                pulses{2,k}(:, 2) = pulses{2,k}(:,2)-pulses{2,k}(1,2);
                                pulses{2,k}(1, :) = [];
                                continue; %infloop is true, so this will exit the while loop
                            elseif command(4)<=currentLine
                                %if the BRANCH command goes backwards, this
                                %stores some information about it in
                                %pulses{2,k} that will later be used the
                                %next time BRANCH is hit
                                if command(2)>hex2dec('E00000')
                                    command(2) = command(2)-hex2dec('E00000');
                                end
                                siz = size(pulses{1,k}, 1);
                                pulses{2,k} = [siz command(2), time];
                                currentLine = command(4);
                            else
                                %if BRANCH goes forward, just move to that
                                %line without a worry
                                currentLine = command(4);
                            end
                            %DONT USE BRANCH TO GO BACKWARDS UNLESS YOU
                            %INTEND FOR IT TO BE AN INFINITE LOOP. IT IS
                            %BAD PROGRAMMING, AND THIS FUNCTION IS NOT
                            %DESIGNED TO HANDLE IT. WEIRD THINGS WILL
                            %HAPPEN.
                            
                        case 7 %LONG_DELAY
                            %same as continue, but waits longer
                            time = time + command(4)*command(5); %increment time
                            lastline = currentLine;
                            currentLine = currentLine + 1; %continue forward
                            continue; %skip the next time increase that comes at the end of the while loop
                            
                        case 8 %WAIT
                            %will be interpreted the same as a STOP
                            %command, essentially ignored
                            %lastline = currentLine;
                            %currentLine = -1;
                            %bStopTemp = true;
                            lastline = currentLine;
                            currentLine = currentLine + 1;
                            lineWait{1,k}(currentLine) = 1;
                            %goes on to next line
                    end
                    time = time + command(5); %increment time
                end
                if time > finalTime
                    bStop = bStopTemp;
                    finalTime = time;
                end
            end
        end
        
        function endPulse = combinePulses(pulses, lineWait)
            %Combines the individual pulse sequences generated by the
            %decompressPulse function, and then tries to shrink them down
            %as much as possible by finding loops and compressing them.
            
            %Identify the maximum amount of time of the normal pulse
            %sequences (non-infinite loops). This is necessary so that
            %if there is an infinite loop, it will know how long to repeat
            %itself in the normal pulse sequence before we convert it into
            %an infinite loop to append to the end.
            tMax = 0;
            for k = 1:size(pulses, 2)
                if ~isempty(pulses{1,k})
                    if pulses{1,k}(end,2) > tMax
                        tMax = pulses{1,k}(end,2);
                    end
                end
            end
            
            %recombine all the pulses together, starting with the first,
            %and build the pulseMat and loopMat matrices
            for i = 1:size(pulses, 2)
                
                %This block of code deals with the case if an infinite
                %loop. Due to how the decompressPulses function works,
                %there can only be one non-empty pulses{2,i}, so all of
                %this will only happen once at most.
                
                %Clear everything before the infinite loop if it doesn't
                %have any time attached. I was getting problems before
                %where it would start my code with a bunch of junk bits all
                %at time = 0, so I included this. I don't think I need it
                %anymore, but I left it in anyways just in case.
                if ~isempty(pulses{2,i})
                    if ~any(pulses{1,i}(:,2)~=0)
                        pulses{1,i} = [];
                    end
                end
                
                if isempty(pulses{1,i})&&isempty(pulses{2,i})
                    %if this bit just doesn't exist, set it to 0 and go on
                    pulses{1,i} = [0 0];
                    
                elseif isempty(pulses{1,i})&&~isempty(pulses{2,i})
                    %runs if the infinite loop starts with the very first
                    %line for that bit (when pulses{1,i} is empty but an
                    %infinite loop exists)
                    
                    %the program needs 2 lines of infinite loop to work, so
                    %it generates 2 lines if it somehow only gets one. A
                    %1-line program that makes an infinite loop will still
                    %generate 2 lines in pulses{2,i}, so this should never
                    %happen, but just in case
                    if size(pulses{2,i}, 1)==1
                        dat = pulses{2,i}(1,1);
                        pulses{2,i} = [dat 500; dat 1000];
                    end
                    
                    %start pulses{1,i} as one instance of the loop starting
                    %at time t = 0, bringing the first line of the infinite
                    %loop to the end of pulses{1,i}
                    pulses{1,i} = [pulses{2,i}(2:end,1), (pulses{2,i}(2:end,2)-pulses{2,i}(2,2))];
                    pulses{1,i}(end+1,:) = [pulses{1,i}(1,1), (pulses{2,i}(end,2)-pulses{2,i}(1,2))];
                    
                    %store pulses{2,i} in loopMat for later
                    loopMat = pulses{2,i};
                    
                    %convert pulses{2,i} into an infinite loop that can be
                    %appended as many times as needed onto the end of
                    %pulses{1,i}
                    pulses{2,i}(2:end,2) = pulses{2,i}(2:end,2)-pulses{2,i}(1:end-1,2);
                    pulses{2,i}(1,:) = [];
                    pulses{2,i} = [pulses{2,i}(end,:); pulses{2,i}(1:end-1,:)];
                    pulses{2,i}(:,2) = cumsum(pulses{2,i}(:,2));
                    
                    %append pulses{2,i} to pulses{1,i} until this pulse
                    %sequence is longer than that for any other bit. This
                    %makes it so we can freely stick the infinite loop on
                    %at the end without messing stuff up
                    while pulses{1,i}(end,2)<=tMax
                        pulses{1,i} = [pulses{1,i}; [pulses{2,i}(:,1), (pulses{2,i}(:,2)+pulses{1,i}(end,2))]];
                    end
                    
                elseif ~isempty(pulses{2,i})
                    %the program needs 2 lines of infinite loop to work, so
                    %it generates 2 lines if it somehow only gets one. A
                    %1-line program that makes an infinite loop will still
                    %generate 2 lines in pulses{2,i}, so this should never
                    %happen, but just in case
                    if size(pulses{2,i}, 1)==1
                        dat = pulses{2,i}(1,1);
                        pulses{2,i} = [dat 500; dat 1000];
                    end
                    
                    %store pulses{2,i} in loopMat for later
                    loopMat = pulses{2,i};
                    
                    %convert pulses{2,i} into an infinite loop that can be
                    %appended as many times as needed onto the end of
                    %pulses{1,i}
                    pulses{2,i}(2:end,2) = pulses{2,i}(2:end,2)-pulses{2,i}(1:end-1,2);
                    pulses{2,i}(1,:) = [];
                    pulses{2,i} = [pulses{2,i}(end,:); pulses{2,i}(1:end-1,:)];
                    pulses{2,i}(:,2) = cumsum(pulses{2,i}(:,2));
                    
                    %append pulses{2,i} to pulses{1,i} until this pulse
                    %sequence is longer than that for any other bit. This
                    %makes it so we can freely stick the infinite loop on
                    %at the end without messing stuff up
                    while pulses{1,i}(end,2)<tMax
                        pulses{1,i} = [pulses{1,i}(1:end-1, :); [pulses{2,i}(:,1), (pulses{2,i}(:,2)+pulses{1,i}(end,2))-pulses{2,i}(1,2)]];
                    end
                end %end infinite loop pre-processing
                
                %Turn all the 0's denoting an 'off' bit to NaN to make it
                %easier to deal with. Keeps a 0-time as a 0;
                pulses{1,i}(pulses{1,i}==0) = NaN;
                if isnan(pulses{1,i}(1,2))
                    pulses{1,i}(1,2) = 0;
                end
                
                %build the pulseMat variable, storing each bit's pulse
                %sequence as one large matrix
                if ~exist('pulseMat', 'var')
                    pulseMat = fliplr(pulses{1,i}); %we want time to come first, then the bit, so fliplr
                else
                    %append the next pulse sequence onto the previous ones,
                    %sliding the bit information over into a column
                    %corresponding to which bit it is
                    pulseMat = [pulseMat, zeros(size(pulseMat, 1), size(pulses{1,i}, 2)-1);...
                        pulses{1,i}(:,2), zeros(size(pulses{1,i},1), size(pulseMat, 2)-1), pulses{1,i}(:,1)]; %#ok<AGROW>
                end
            end %end building the pulseMat and loopMat matrices
            
            % here now lineWait does not include the flag lines for the
            % duration = 0 state, so it has one less element per bit than
            % pulseMat has
            waitList = []; % zeros(size(pulseMat,1));
            for i=1:size(pulses,2)
               % get the same format then as pulseMat for the lineWait
               waitList = [waitList lineWait{i} 0];
            end
            %waitList
            %pulseMat
            
            %NOTE: AT THIS POINT, NaN REPRESENTS A COMMAND TO SWITCH A BIT
            %TO 0, AND A '0' IN THIS MATRIX ONLY REPRESENTS THAT THE BIT IS
            %SUPPOSED TO RETAIN ITS INTENDED VALUE WHILE COMMANDS ARE GIVEN
            %TO OTHER BITS
            
            if exist('pulseMat', 'var') %if we only had a single sequence of just an infinite loop, pulseMat would not exist yet
                
                %sort pulseMat so that each event happens in chronological
                %order
                [~, I] = sort(pulseMat(:,1)); %get an index vector describing how to sort pulseMat chronologically
                pulseMat = pulseMat(I, :); %sort the entire matrix based on that index vector
                
                % sort waitList in the same order with the index I
                try
                waitList = waitList';
                waitList = waitList(I);
                catch
                end
                %run up the pulseMat matrix from the buttom, consolidating
                %simultaneous commands to separate bits into one line
                len = size(pulseMat, 1);
                for k = 1:len-1
                    t = len+1-k; %use t as the index instead of k so we go from the bottom up
                    if pulseMat(t,1) == pulseMat(t-1, 1); %if the time of a row equals that of the one above, they are simultaneous
                        pulseMat(t-1,2:end) = pulseMat(t-1, 2:end)+pulseMat(t, 2:end); %add the bit commands for the two lines
                        pulseMat(t, :) = []; %delete the bottom of the two commands
                        
                        % do the same for waitList, just deletion part is
                        % needed since it only has a single column
                        try
                        waitList(t) = [];
                        catch
                        end
                    end
                end
                
                %run down the pulseMat matrix from the top, setting every
                %unassigned bit to the value it had above. This is the
                %crucial step. It allows each bit to retain its own value
                %while commands are given to other bits, and change its
                %value only when it is supposed to
                len = size(pulseMat, 1); %this might have changed due to the last set of instructions
                for k = 2:len %vertical index
                    for r = 2:size(pulseMat, 2) %horizontal index
                        if pulseMat(k,r)==0
                            pulseMat(k,r) = pulseMat(k-1,r);
                        end
                    end
                end
                % no change to waitList from this operation
                
                %final processing on the pulseMat matrix, getting it ready
                %to be re-compressed.
                pulseMat(isnan(pulseMat))=0; %convert NaN's back into 0's, as they should be
                pulseMat = [pulseMat(:,1), sum(pulseMat(:, 2:end), 2)];
                % no change to waitList from this operation

                
                %add two columns for the command code and instruction-specific data
                pulseMat = [pulseMat(:,1) zeros(size(pulseMat, 1), 2) pulseMat(:, 2:end)];
                
                pulseMat = [(0:(size(pulseMat, 1)-1))' pulseMat]; %add line numbers to the front of pulseMat
                % no change to waitList from this operation
                % though we could add the wait command here instead of
                % having it be a zero here ("uncompressed")
                
                %change the time column so that it displays a duration for
                %each command instead of showing the absolute time each
                %command happens
                pulseMat(1:end-1,2) = pulseMat(2:end, 2)-pulseMat(1:end-1, 2);
                %pulseMat(end, 2) = 100;
                pulseMat(end, 2)=0; % changed 11-28-11 for more accurate reconcile to desired result
                % no change to waitList from this operation, but....
                
                % new 5-6-2013
                % the code above always sets the commands of every line
                % equal to a 0 for CONTINUE since it is "decompressed".
                % However, we want WAIT commands preserved:
                try
                pulseMat(:,3) = waitList(:)*8;
                catch
                end
                
                %Remove any situation where two subsequent lines of code
                %are completely identical, just not combined for some
                %reason.
                bChanged = false;
                for x = size(pulseMat, 1):-1:2
                    if isequal(pulseMat(x,3:end), pulseMat(x-1,3:end))
                        pulseMat(x-1,2) = pulseMat(x,2)+pulseMat(x-1,2);
                        pulseMat(x,:) = [];
                        try
                        waitList(x) = [];
                        catch
                        end
                        bChanged = true;
                    end
                end
                if bChanged == true
                    pulseMat(:,1) = (0:size(pulseMat, 1)-1)';
                end

                %pulseMat = addShortPulses(pulseMat);
                %convert delays longer than 500 ms into LONG_DELAYs, which
                %is required. The pulseblaster will only accept CONTINUEs
                %of up to 640 ns. Do this twice, just to make sure, because
                %it messes up sometimes.
%                 pulseMat = convertLongDelay(pulseMat, 0);
%                 pulseMat = convertLongDelay(pulseMat, 0);
                
                %run through looking for loops to help compress the code.
                %This is important because it is easy to write code using
                %loops that expands out to be thousands of lines long
                %without loops, and that can crash the pulseblaster and
                %matlab
                pulseMat = consolidateLoops(pulseMat, pulseMat, 0);
                pulseMat = fixLoopData(pulseMat);

            end %end pulseMat processing
            
            %Now, process the loopMat in the same way
            if exist('loopMat', 'var')
                
                %convert times from being an absolute time to a duration
                %for each command, same as with pulseMat
                loopMat(1:end-1,2) = loopMat(2:end, 2)-loopMat(1:end-1, 2);
                
                loopMat = fliplr(loopMat); %time needs to go first, then the bit information
                loopMat(end,:) = [];%clear this line, as it now comes at the end
                
                loopMat = [(0:size(loopMat, 1)-1)', loopMat(:,1), zeros(size(loopMat, 1), 2), loopMat(:,2)];
                
                %loopMat = addShortPulses(loopMat);
                %convert delays longer than 500 ms into LONG_DELAYs, which
                %is required. The pulseblaster will only accept CONTINUEs
                %of up to 640 ns
                loopMat = convertLongDelay(loopMat, loopMat(1,1));
                
                loopMat(end, 3) = 6;            %turn the last command issued into a BRANCH
                loopMat(end,4) = loopMat(1,1);  %and make it point back to the first line to complete the loop
                
                %run through looking for loops to help compress the code.
                %This is important because it is easy to write code using
                %loops that expands out to be thousands of lines long
                %without loops, and that can crash the pulseblaster and
                %matlab
                loopMat = consolidateLoops(loopMat, loopMat, loopMat(1,1));
                
                %append the infinite loop onto the end of pulseMat
                if exist('pulseMat', 'var')
                    loopMat(end, 4) = size(pulseMat, 1);
                    pulseMat = [pulseMat; loopMat];
                    pulseMat(:, 1) = (0:(size(pulseMat, 1)-1))';
                else
                    pulseMat = loopMat;
                end
                pulseMat = fixLoopData(pulseMat);
            end
            
            function out = addShortPulses(inpulse)
                out = inpulse;
                for q = size(out, 1):-1:1
                    if mod(out(q,2), 10)~=0 && out(q,2)>10
                        out = [out(1:q-1, :); [out(q,1), out(q,2)-mod(out(q,2), 10), out(q,3:end)];...
                            [0, mod(out(q,2), 10), out(q, 3:end)]; out(q+1:end, :)];
                    end
                    if out(q,2) == 10
                        out = [out(1:q-1, :); [out(q,1), 6, out(q,3:end)];...
                            [0, 4, out(q, 3:end)]; out(q+1:end, :)];
                    end
                end
                out(:,1) = (0:(size(out, 1)-1))';
            end
            
            function out = consolidateLoops(inpulse, oldInPulse, startLine)
                %Runs through the pulse sequence given and finds loops in
                %the code than can be condensed down. inpulse and
                %oldInPulse should be the same matrix when you call it:
                %oldInPulse is needed to make sure that everything is
                %condensed down as far as possible.
                %
                %The general idea for this program is that it checks if a
                %certain number of lines are equal to the next block of the
                %exact same size. By starting with the largest reasonable
                %number (a third of the total length) and decreasing the
                %number of lines every time, it can find loops as
                %efficiently as possible. If a loop is found, the program
                %stops and just re-calls itself recursively to avoid errors
                %caused by changing the size of the matrix.
                %
                %Unfortunately, this does not always result in the smallest
                %loops possible, which means there are more lines of code
                %being passed to the pulseblaster. To fix this, every time
                %a loop is discovered, the program checks if shrinking the
                %original code by the new loop instead of any older ones
                %would condense it more.
                %
                %As an example, repeating a 5-line loop 100 times would
                %make code that is 500 lines long. If we just condensed it
                %from the largest loop size possible, the first found loop
                %would be 130 lines long, with 10 left over at the end. The
                %next iteration finds a loop 45 lines long, then one 15
                %lines long, then stops, leaving code that is around 30~40
                %lines total. If it instead tried to compress by the 15
                %line loop from the start, it would end up with only 20
                %lines of code, so this function attempts that every time a
                %loop is found to make the smallest code possible.
                
                %check input arguments
                if isempty(inpulse);
                    out = [];
                    return
                end
                
                %loop over the number of lines checked, starting with the
                %largest value and going down
                n = floor(size(inpulse, 1)/3):-1:3;
                for numLines = n
                    %loop through the matrix checking every block of
                    %lines against the one immediately after
                    for in1 = 1:(size(inpulse, 1)-2*numLines-1)
                        %if a block is equal to the next block, then you
                        %may have a loop
                        try
                            b1 = isequal(inpulse(in1:(in1+numLines), 2:end), inpulse((in1+numLines+1):(in1+2*numLines+1), 2:end));
                        catch err %#ok<NASGU>
                            b1 = false;
                            clear err
                        end
                        if b1
                            %condense the loop
                            looptimes = 1;
                            while true
                                inpulse((in1+numLines+1):(in1+2*numLines+1), :) = [];
                                looptimes = looptimes + 1;
                                try
                                    if ~isequal(inpulse(in1:(in1+numLines), 2:end), inpulse((in1+numLines+1):(in1+2*numLines+1), 2:end))
                                        break;
                                    end
                                catch err %#ok<NASGU>
                                    clear err
                                    break;
                                end
                            end
                            %add the LOOP and END_LOOP commands, taking
                            %into account the possibility of having a
                            %LONG_DELAY at the beginning or end of the
                            %loop
                            if inpulse(in1,3)==7 && inpulse(in1,4)>=2
                                inpulse = [inpulse(1:in1-1,:); [0, 500, 2, looptimes, inpulse(in1, 5)];...
                                    [inpulse(in1,1:3), (inpulse(in1,4)-1), inpulse(in1,5)]; inpulse(in1+1:end,:)];
                                if inpulse(in1+numLines+1, 3)==7 && inpulse(in1+numLines+1, 4)>=2
                                    inpulse(in1+numLines+1, 4) = inpulse(in1+numLines+1, 4)-1;
                                    inpulse = [inpulse(1:in1+numLines+1, :); [0, 500, 3, in1, inpulse(in1+numLines+1, 5)]; inpulse(in1+numLines+2:end, :)];
                                    inpulse(:,1) = (0:size(inpulse, 1)-1)'+startLine;
                                    inpulse(in1+numLines+2, 4) = inpulse(in1,1);
                                else
                                    inpulse(in1+numLines+1, 3) = 3;
                                    inpulse(:,1) = (0:size(inpulse, 1)-1)'+startLine;
                                    inpulse(in1+numLines+1, 4) = inpulse(in1,1);
                                end
                            else
                                inpulse(in1, 3) = 2;
                                inpulse(in1, 4) = looptimes;
                                if inpulse(in1+numLines, 3)==7 && inpulse(in1+numLines, 4)>=2
                                    inpulse(in1+numLines, 4) = inpulse(in1+numLines, 4)-1;
                                    inpulse = [inpulse(1:in1+numLines, :); [0, 500, 3, in1, inpulse(in1+numLines, 5)]; inpulse(in1+numLines+1:end, :)];
                                    inpulse(:,1) = (0:size(inpulse, 1)-1)'+startLine;
                                    inpulse(in1+numLines+1, 4) = inpulse(in1,1);
                                else
                                    inpulse(in1+numLines, 3) = 3;
                                    inpulse(:,1) = (0:size(inpulse, 1)-1)'+startLine;
                                    inpulse(in1+numLines, 4) = inpulse(in1,1);
                                end
                            end



                            %check if the original matrix can be
                            %condensed better by eschewing
                            %previously-found loops and starting with
                            %this size loop instead. This works exactly
                            %the same as the previous part
                            tempPulse = oldInPulse;
                            for in2 = (1:size(tempPulse, 1)-2*numLines-1)
                                try
                                    b2 = isequal(tempPulse(in2:(in2+numLines), 2:end), tempPulse((in2+numLines+1):(in2+2*numLines+1),2:end));
                                catch err %#ok<NASGU>
                                    b2 = false;
                                    clear err
                                end
                                if b2
                                    looptimes = 1;
                                    while true
                                        tempPulse((in2+numLines+1):(in2+2*numLines+1), :) = [];
                                        looptimes = looptimes+1;
                                        try 
                                            if~isequal(tempPulse(in2:(in2+numLines), 2:end), tempPulse((in2+numLines+1):(in2+2*numLines+1), 2:end))
                                                break;
                                            end
                                        catch err %#ok<NASGU>
                                            clear err
                                            break
                                        end
                                    end
                                    %add LOOP and END_LOOP
                                    %commands, taking into account
                                    %the possibility of LONG_DELAYs
                                    if tempPulse(in2,3)==7 && tempPulse(in2,4)>=2
                                        tempPulse = [tempPulse(1:in2-1,:); [0, 500, 2, looptimes, tempPulse(in2, 5)];...
                                            [tempPulse(in2,1:3), (tempPulse(in2,4)-1), tempPulse(in2,5)]; tempPulse(in2+1:end,:)];
                                        if tempPulse(in2+numLines+1, 3)==7 && tempPulse(in2+numLines+1, 4)>=2
                                            tempPulse(in2+numLines+1, 4) = tempPulse(in2+numLines+1, 4)-1;
                                            tempPulse = [tempPulse(1:in2+numLines+1, :); [0, 500, 3, in2, tempPulse(in2+numLines+1, 5)]; tempPulse(in2+numLines+2:end, :)];
                                            tempPulse(:,1) = (0:size(tempPulse, 1)-1)'+startLine;
                                            tempPulse(in2+numLines+2, 4) = tempPulse(in2,1);
                                        else
                                            tempPulse(in2+numLines+1, 3) = 3;
                                            tempPulse(:,1) = (0:size(tempPulse, 1)-1)'+startLine;
                                            tempPulse(in2+numLines+1, 4) = tempPulse(in2,1);
                                        end
                                    else
                                        tempPulse(in2, 3) = 2;
                                        tempPulse(in2, 4) = looptimes;
                                        if tempPulse(in2+numLines, 3)==7 && tempPulse(in2+numLines, 4)>=2
                                            tempPulse(in2+numLines, 4) = tempPulse(in2+numLines, 4)-1;
                                            tempPulse = [tempPulse(1:in2+numLines, :); [0, 500, 3, in2, tempPulse(in2+numLines, 5)]; tempPulse(in2+numLines+1:end, :)];
                                            tempPulse(:,1) = (0:size(tempPulse, 1)-1)'+startLine;
                                            tempPulse(in2+numLines+1, 4) = tempPulse(in2,1);
                                        else
                                            tempPulse(in2+numLines, 3) = 3;
                                            tempPulse(:,1) = (0:size(tempPulse, 1)-1)'+startLine;
                                            tempPulse(in2+numLines, 4) = tempPulse(in2,1);
                                        end
                                    end
                                end
                            end

                            %if the original matrix is better condensed
                            %by the new loop size, then use that result
                            %instead of what we have gotten through our
                            %recursive methods
                            if size(tempPulse, 1)<size(inpulse,1)
                                inpulse = tempPulse;
                            end

                            %Every time a loop is found, the program
                            %must quit out of all for- and while-loops
                            %(hence the 'return') and redo the loops,
                            %as they are dependant on the old matrix
                            %size, which has changed. Thus, recursion
                            inpulse = consolidateLoops(inpulse, oldInPulse, startLine);
                            inpulse(:,1) = (0:size(inpulse, 1)-1)'+startLine;
                            out = inpulse;
                            return
                        end
                    end
                end
                out = inpulse;
            end %end consolidateLoops
            
            function outpul = convertLongDelay(inpul, startLine)
                %finds any instance in which a bit configuration is to be
                %held for longer than 500 ns, and turns it into a
                %LONG_DELAY so that the pulseblaster doesn't get mad at you
                
                %check for input arguments
                if isempty(inpul)
                    outpul = [];
                    return
                end
                
                bChange = false; %check to see if things change, so that we know if we have to redo the line numbers
                for h = 1:size(inpul,1)
                    if inpul(h,2)>500 %check how long a CONTINUE is, and fix it if it is too long
                        inpul(h,3) = 7;
                        
                        %if the standard LONG_DELAY I use (base time of 500
                        %ns) does not last the exact right amount of time,
                        %then we need to add a continue statement at the
                        %end to make it just right
                        inpul(h,4) = floor(inpul(h,2)/500);
                        if inpul(h,2)==inpul(h,4)*500 %if it's perfect
                            inpul(h,2) = 500;
                        else
                            inpul = [inpul(1:h,:); [0 (inpul(h,2)-(inpul(h,4)*500)) 0 0 inpul(h,5)]; inpul(h+1:end,:)];
                            inpul(h,2) = 500;
                        end
                        bChange = true; %something has been changed, so we need to redo the line numbers
                    end
                end
                %fix line numbers
                if bChange
                    inpul(:,1) = (0:(size(inpul,1)-1))'+startLine;
                end
                outpul = inpul;
            end %end convertLongDelay
            
            function outpulse = fixLoopData(inpulse)
                %Fixes loops so that they go back to the correct line after
                %everything has been condensed.
                
                %Get the line numbers for the start and end of every loop
                loops = find(inpulse(:,3)==2);
                loopEnds = find(inpulse(:,3)==3);
                
                if isempty(loops)
                    %If there are no loops, then return
                    outpulse = inpulse;
                    return;
                elseif length(loops)==1
                    %If there is only one loop, this is very easy.
                    inpulse(loopEnds, 4) = loops-1;
                    outpulse = inpulse;
                    return
                end
                if length(loops) ~= length(loopEnds) %We clearly need the same number of each
                    error(['Number of LOOPs does not match the number of END_LOOPs. Try to find the bug in the '...
                        'consolidateLoops function.']);
                end
                
                %Starting with the last END_LOOP command, go up the list of
                %loops connecting each LOOP with its END_LOOP. Will account
                %for nested loops.
                for n = fliplr(loopEnds')
                    indStart = find(loops<n, 1, 'last');
                    indEnd = find(loopEnds == n)-1;
                    while true
                        if indEnd < 1
                            inpulse(n, 4) = loops(indStart)-1;
                            loops(indStart) = [];
                            break
                        end
                        if loops(indStart) > loopEnds(indEnd)
                            inpulse(n, 4) = loops(indStart)-1;
                            loops(indStart) = [];
                            break
                        else
                            indStart = indStart - 1;
                            indEnd = indEnd - 1;
                        end
                    end
                end
                outpulse = inpulse;
            end
            for k = 1:size(pulseMat, 1)
                if pulseMat(k, 3)==7 && pulseMat(k, 4)==1
                    pulseMat(k, 3:4) = [0, 0];
                end
            end
            endPulse = pulseMat;
        end
        
        function Instruction = compressPulse(endPulse)
            %Reduces the large array given by combinePulses into the format
            %expected by loadToPulseblaster.
            
            %Initialize the output array
            Instruction = zeros(size(endPulse,1), 5);
            Instruction(:,1) = endPulse(:,1); %move line numbers over to the output exactly as they are
            Instruction(:,2) = endPulse(:, 5);
            if endPulse(end, 3)~=6
                Instruction(end, 2) = 0;
            end
            
            Instruction(:,3) = endPulse(:,3); %copy commands over perfectly
            if Instruction(end,3)~=6
                Instruction(end, 3) = 1; %if there is no infinite loop, then insert a STOP at the end to keep the program from looping back
            end
            Instruction(:,4) = endPulse(:,4); %copy over instruction-specific data
            Instruction(:,5) = endPulse(:,2); %copy over times
            Instruction(Instruction(:,5)==0,:) = [];
            Instruction((Instruction(:,5)>= 5), 2) = ...
                Instruction((Instruction(:,5)>= 5), 2)+hex2dec('E00000');
        end
        
        function Instruction = loadPulse(varargin)
            %Straight-forward function that loads a set of commands stored
            %in a text file and returns it. Takes a filename(optional). To
            %save this to currentInstruction, just call
            %obj.setCurrentInstruction with no arguments instead.
            
            %if no arguments are passed in, then get the filename from a
            %uigetfile dialog box
            if nargin == 0
                [filename pathname] = uigetfile('*.txt', 'Select Pulse Sequence',...
                    'C:\Users\lab\Documents\code\MATLAB\NewPulseBlaster\SavedPulseSequences\');
                varargin{1} = [pathname filename];
            end
            
            %load and return the information stored in the requested file
            if ischar(varargin{1})
                fid = fopen(varargin{1});
                if fid == -1
                    Instruction = [];
                    return;
                end
                dat = textscan(fid, '%f %f %f %f %f'); %read out the array into a variable
                fclose(fid);
                Instruction = zeros(length(dat{1}), 5); %initialize the output array
                
                %I think textscan returns a cell array, each containing one
                %column from the file, so I programmed that in. If this is
                %incorrect and it just outputs a matrix, then that is
                %accounted for too.
                if ~iscell(dat)
                    Instruction = dat;
                else
                    for i = 1:length(dat{1})
                        Instruction(i, 1) = dat{1}(i);
                        Instruction(i, 2) = dat{2}(i);
                        Instruction(i, 3) = dat{3}(i);
                        Instruction(i, 4) = dat{4}(i);
                        Instruction(i, 5) = dat{5}(i);
                    end
                end
            end
        end
        
        function Instruction = loadESRPulse(varargin)
            % this is the version of the loadPulse() function that is
            % for pulse sequences with a duration (5th column) based on a string
            % expression to be evaluated with variables set to values
            % so it must return a cellArray not a numerical array
            
            %load and return the information stored in the requested file
            %Newvarargin=cellstr(varargin{1}); % new for Labview pulse ESR builder
            varargin{1}
            if ischar(varargin{1})
                fid = fopen(varargin{1});
                %fid = fopen(Newvarargin{1}); % new for Labview pulse ESR builder
                if fid == -1
                    Instruction = [];
                    return;
                end
                Instruction = textscan(fid, '%f %f %f %s %s')
                %Instruction = textscan(fid, '%f %f %f %f %s'); %read out the array into a variable
                fclose(fid);
            end
        end
        
        function outPulse = appendPulses(varargin)
            %Append any number of pulses together and output the result.
            %Same as vertcat, except performs checks to make sure that only
            %proper pulse sequences are appended to each other.
            
            if nargin == 1
                if isnumeric(varargin{1})
                    if size(varargin{1}, 2)==5
                        outPulse = varargin{1};
                        return;
                    else
                        outPulse = [];
                        return;
                    end
                else
                    outPulse = [];
                    return;
                end
            elseif nargin == 0
                outPulse = [];
                return;
            end
            outPulse = [];
            for k = 1:nargin
                if isnumeric(varargin{k})
                    if size(varargin{k}, 2)==5
                        if isempty(outPulse)
                            outPulse = varargin{k};
                        else
                            %if the last line of outPulse is a STOP command
                            %and we want to append another set of commands,
                            %then we must delete that STOP line first
                            if outPulse(end, 3)==1
                                outPulse(end,:) = []; %#ok<AGROW>
                            end
                            
                            %append the next pulse sequence
                            varargin{k}(logical((varargin{k}(:,3)==3) + (varargin{k}(:,3)==4) + (varargin{k}(:,3)== 6)), 4) = ...
                                varargin{k}(logical((varargin{k}(:,3)==3) + (varargin{k}(:,3)==4) + (varargin{k}(:,3)== 6)), 4) + size(outPulse, 1);
                            outPulse = vertcat(outPulse, varargin{k}); %#ok<AGROW>
                        end
                    end
                end
            end
        end
        
        function outpulse = bitControl(inpulse, onOff, varargin)
            %Turn bits on and off in a pulse sequence manually.
            %
            %Runs through the program, turning individual bits on or off
            %throughout the entire program. Takes an Nx5 pulse sequence
            %matrix, either the string 'on' or 'off', and the number of
            %each bit (0-20).
            %
            %If a bit is turned on, this function will make sure that the
            %pulse sequence enters an infinite loop holding that bit on. If
            %the end of the sequence was an infinite loop with just that
            %bit on, then the BRANCH command will be replaced by a STOP.
            
            %Perform checks
            if nargin <=2 || isempty(varargin{1})
                outpulse = inpulse;
                return;
            end
            if ~ischar(onOff)
                error('2nd input must either be ''on'' or ''off.''');
            end
            if ~isnumeric(inpulse) || size(inpulse, 2)~=5
                error('1st input must be an Nx5 numeric pulse sequence.');
            end
            if nargin == 3
                if ~isnumeric(varargin{1}) || (size(varargin{1},1)>1 && size(varargin{1},2)>1)
                    error('Extra inputs must all be single numeric values or a single vector of values')
                end
                bit = varargin{1};
            else
                bit = NaN(1,(nargin-2));
                for k = 1:(nargin-2)
                    if ~isnumeric(varargin{k}) || length(varargin{k})~=1
                        error('Extra inputs must all be single numeric values or a single vector of values')
                    end
                    bit(k) = varargin{k};
                end
            end
            if max(bit) > 20 || min(bit) < 0
                error('Only bits 0-20 may be manually turned off or on. Bits 21-23 are reserved.')
            end
            %Loop through, turning the specified bits on or off
            for n = 1:size(inpulse, 1)
                dat = fliplr(dec2bin(inpulse(n,2)));
                for m = 1:length(bit)
                    switch onOff
                        case 'on'
                            if length(dat)<bit(m)+1
                                inpulse(n,2) = inpulse(n,2)+2^bit(m);
                            elseif strcmp(dat(bit(m)+1), '0')
                                inpulse(n,2) = inpulse(n,2)+2^bit(m);
                            end
                            %If the last command is a stop, then we turn it
                            %into an infinite loop
                            if (n == size(inpulse, 1)) && (inpulse(end,3)==1)
                                inpulse(end,:) = [inpulse(end, 1:2), 6, inpulse(end,1), 500];
                            end
                        case 'off'
                            if length(dat)<bit(m)+1
                                continue;
                            elseif strcmp(dat(bit(m)+1), '1')
                                inpulse(n,2) = inpulse(n,2) - 2^bit(m);
                            end
                            if inpulse(n,2) == hex2dec('E00000')
                                inpulse(n,2) = 0;
                            end
                    end
                end
            end
            inpulse(inpulse(:,2)<hex2dec('E00000'), 2) = inpulse(inpulse(:,2)<hex2dec('E00000'), 2)+hex2dec('E00000');
            inpulse(inpulse(:,2) == hex2dec('E00000'), 2) = 0;
            if inpulse(end,3) == 6
                if (inpulse(end,4)==inpulse(end, 1)) && (inpulse(n,2)==0)
                    inpulse(end,:) = [inpulse(end,1), 0, 1, 0, 100];
                end
            end
            outpulse = inpulse;
        end
                
        function runPulse()
            %Runs the loaded pulse sequence, with a check to make sure it worked properly
            err = pb_start();
            if err < 0
                error(['Pulseblaster did not load program correctly. Make sure that the instructions are'...
                    ' correct, then try again']);
            end
        end
        
        function stopPulse()
            %stops the running pulse sequence, with a check to make sure it
            %stopped correctly. If it didn't, I don't know what the error
            %could have been. pb_stop may not even return anything.
            err = pb_stop();
            if err < 0
                error('Pulseblaster unable to stop. Maybe it was not actually running? I dont know');
            end
        end
        
        function clearPulseblaster()
            %Clear out the pulseblaster and close it, completely reseting
            %it so it must be initialized again and no pulse sequences are
            %stored on it.
            pb_stop();
            pb_close();
        end
        
        function resetPulseblaster()
            %calls the reset function. I don't know the details of this,
            %but I am pretty sure it stops the running program and clears
            %all loaded pulse sequences without making the user
            %re-initialize the pulseblaster.
            calllib('spinapi', 'pb_reset');
        end
        
        function saveESRPulse(varargin)
            % requires input filename, as this will only be called by the
            % ESRsave sequence in the modified pulse builder
            % other argument is the actual data to save
            xx=varargin{2};
            [rows,~]=size(xx);
            fid = fopen(varargin{1}, 'wt');
            for i = 1:rows
                fprintf(fid,'%i\t', xx{i,1:end-1});
                fprintf(fid,'%s\n', xx{i,end});
            end
            fclose(fid);
        end
    end
end