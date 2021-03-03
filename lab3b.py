#!/usr/bin/env python3
import csv, argparse, sys

def parse(filename):
    free_inodes = [] #List of free inode numbers
    is_free_inodes = {}
    free_blocks = [] #List of free block numbers
    is_free_blocks = {}
    superblock = {} #Superblock summary
    group = {} #Group summary -- Note: There will only be one group
    inode_summaries = [] #Inode summaries -- List of dictionaries
    dir_entries = [] #Directory entries -- List of dictionaries
    indirect= [] #Indirect blocks -- List of dictionaries
    try:
        file = open(filename, newline='')
    except:
        sys.stderr.write('Error: Could not open given filename: ' + filename + "\n")
        exit(1)
    data = csv.reader(file, delimiter=',', quotechar= '|' )
    for i in data:
        if(i[0] == "BFREE"):
            free_blocks.append(int(i[1]))
            is_free_blocks[int(i[1])] = True
        elif(i[0] == "IFREE"):
            free_inodes.append(int(i[1]))
            is_free_inodes[int(i[1])] = True
        elif(i[0] == "SUPERBLOCK"):
            superblock["num_blocks"] =  int(i[1]) #Total number of blocks
            superblock["num_inodes"] =  int(i[2]) #Total number of inodes
            superblock["block_size"] = int(i[3])
            superblock["inode_size"] =  int(i[4])
            superblock["blocks_per_group"] = int(i[5]) #Maximum value, real might be less
            superblock["i_nodes per group"] = int(i[6]) #Maximum value, real might be less
            superblock["first_inode"] = int(i[7])
        elif(i[0] == "GROUP"):
            group["number"] = int(i[1])
            group["num_blocks"] = int(i[2])
            group["num_inodes"] = int(i[3])
            group["free_blocks"] = int(i[4])
            group["free_inodes"] = int(i[5])
            group["block_bitmap"] = int(i[6])
            group["inode_bitmap"] = int(i[7])
            group["inode_table"] = int(i[8])
        elif(i[0] == "INODE"):
            is_free_inodes[int(i[1])] = False
            inode = {}
            inode["number"] = int(i[1])
            inode["type"] = i[2]
            inode["mode"] = int(i[3])
            inode["owner"] = int(i[4])
            inode["group"] = int(i[5])
            inode["link_count"] = int(i[6])
            inode["last_change"] =  i[7]
            inode["modification"] = i[8]
            inode["last_access"] =  i[9]
            inode["file_size"] = i[10]
            inode["num_blocks"] = i[11]
            inode["blocks"] = list(map(int, i[12:])) #Figure this out later -> bug
            for b in inode["blocks"]:
                is_free_blocks[b] = False
            inode_summaries.append(inode)
        elif(i[0] == "DIRENT"):
            dirent = {}
            dirent["parent"] = int(i[1])
            dirent["offset"] = int(i[2])
            dirent["inumber"] = int(i[3])
            dirent["entry_len"] = int(i[4])
            dirent["name_len"] = int(i[5])
            dirent["name"] = i[6]
            dir_entries.append(dirent)
        elif(i[0] == "INDIRECT"):
            indir = {}
            indir["inumber"] = int(i[1])
            indir["level"] = int(i[2])
            indir["offset"] = int(i[3])
            indir["indir"] = int(i[4])
            indir["block_num"] = int(i[5])
            indirect.append(indir)
            is_free_blocks[int(i[5])] = False
    return free_inodes, free_blocks, superblock, group, inode_summaries, dir_entries, indirect, is_free_blocks, is_free_inodes

def calculate_offset(i):
    if(i == 12): #Single indirect
        return 12, "INDIRECT "
    elif(i == 13):
        return 268, "DOUBLE INDIRECT "
    elif(i == 14):
        return 65804, "TRIPLE INDIRECT "
    else:
        return 0, ""

def calculate_indirect_offset(i):
    if (i == 1):
        return 12, "INDIRECT"
    elif (i == 2):
        return 268, "DOUBLE INDIRECT"
    elif (i == 3):
        return 65804, "TRIPLE INDIRECT"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",type = str, nargs = "?")
    args = parser.parse_args()
    free_inodes, free_blocks, superblock, group, inode_summaries, dir_entries, indirect, block_bitmap, inode_bitmap =\
    parse(args.filename)
    reserved = [0,1,2,3,4,5,6,7,64]
    #Check for Data Block Number errors
    max_block = superblock["num_blocks"]
    my_block_bitmap  = {}
    duplicates = [[None for x in range(0)] for y in range(max_block)] 
    for inode in inode_summaries:
        if(inode["mode"] == 0):
            continue
        for j in range(len(inode["blocks"])):
            if(j>14):
                break
            cur_block_num = inode["blocks"][j]
            if cur_block_num==0:
                continue
            #print("cur_block_num = " + str(cur_block_num))
            offset, s = calculate_offset(j)
            message= s + "BLOCK " + str(cur_block_num) + " IN INODE " + str(inode["number"]) + " AT OFFSET " + str(offset)
            #print(message)
            if((cur_block_num < 0) or cur_block_num>max_block):
                print("INVALID "+ s + "BLOCK " + str(cur_block_num) + " IN INODE " + str(inode["number"]) + " AT OFFSET " + str(offset))
            else:
                if(cur_block_num in reserved):
                    print("RESERVED " + s + "BLOCK " + str(cur_block_num) + " IN INODE " + str(inode["number"]) + " AT OFFSET " + str(offset))
                if(block_bitmap[cur_block_num] == True):
                    print("ALLOCATED BLOCK " + str(cur_block_num) +" ON FREELIST")
                my_block_bitmap[cur_block_num] = False #False means allocated, True means free
                duplicates[cur_block_num].append(message)

    for indir_block in indirect:
        block_num = indir_block["block_num"]
        inode_num = indir_block["inumber"]
        level = indir_block["level"]
        offset, s = calculate_indirect_offset(level)
        message= s + " BLOCK " + str(block_num) + " IN INODE " + str(inode_num) + " AT OFFSET " + str(offset)
        if((block_num < 0) or block_num>max_block):
                print("INVALID "+ s + "BLOCK " + str(block_num) + " IN INODE " + str(inode_num) + " AT OFFSET " + str(offset))
        else:
            if(block_num in reserved):
                    print("RESERVED " + s + "BLOCK " + str(block_num) + " IN INODE " + str(inode_num) + " AT OFFSET " + str(offset))
            if(block_bitmap[block_num] == True):
                    print("ALLOCATED BLOCK " + str(cur_block_num) + " ON FREELIST")#Error here
            my_block_bitmap[cur_block_num] = False #False means allocated, True means free
            duplicates[block_num].append(message)
    
    for i in duplicates:
        if len(i)>1:
            for elem in i:
                print("DUPLICATE " + elem)

    for block in my_block_bitmap.keys():
        if((block_bitmap[block] == False) and (my_block_bitmap[block] == True)):
            print("UNREFERENCED BLOCK " + str(block))#Error here


    #Check for inode errors
    for inode in inode_summaries:
        num = inode["number"]
        if((inode["mode"]!=0) and (num in inode_bitmap.keys()) and (inode_bitmap[num] == True) ):
            print("ALLOCATED INODE " + str(num) + " ON FREELIST") #Error here
        elif((inode["mode"]==0) and (num in inode_bitmap.keys()) and (inode_bitmap[num] == False)):
            print("UNALLOCATED INODE " + str(num) + " NOT ON FREELIST") #Error here











if __name__ == "__main__":
    main()