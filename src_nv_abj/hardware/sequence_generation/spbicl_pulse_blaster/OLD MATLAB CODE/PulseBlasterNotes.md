- Pulse blaster is coded to recieve in binary 
    -- We see in the MIT code it's in HEX this is stupid
- We use Branch to go back at the end of the code this is so that we can loop the structure of the pulse sequence 
- Sends a pb_stop() command to inturupt the sequence 
    -- Probably default to clearing out a sequence when done this is when it could just restart a old sequence before the DAQ is ready making garbage 
- We use LOOP to loop pasrt of a sequence to loop through the sequence making xy8 sort of thing 

- When possible default laser to be off

