#!/usr/bin/env python3
import csv

def parse(filename):
    #List of free block numbers
    free_inodes = []
    #List of free inode numbers
    free_blocks = []
    #Superblock summary
    superblock = {}
    #Group summary 
    #Note: There will only be one group
    group = {}
    #Inode summaries
    #List of dictionaries
    inode_summaries = []
    #Directory entries
    #List of dictionaries
    dir_entries = []
    #Indirect blocks
    #List of dictionaries
    indirect= []
    file = open(filename, newline='')
    data = csv.reader(file, delimiter=',', quotechar= '|' )
    for i in data:
        if(i[0] == "BFREE"):
            free_blocks.append(int(i[1]))
        elif(i[0] == "IFREE"):
            free_inodes.append(int(i[1]))
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
            inode["blocks"] = list(map(int, i[12:]))
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
    return free_inodes, free_blocks, superblock, group, inode_summaries, dir_entries, indirect

def calculate_offset(i):
    if(i == 12): #Single indirect
        return 12, "INDIRECT "
    elif(i == 13):
        return 268, "DOUBLE INDIRECT "
    elif(i == 14):
        return 65804, "TRIPLE INDIRECT "
    else:
        return 0, ""

def main():
    free_inodes, free_blocks, superblock, group, inode_summaries, dir_entries, indirect = parse('P3B-test_1.csv')
    reserved = [0,1,2,3,4,5,6,7,64]
    # for i in indirect:
    #     print("Indirect block with block number" + str(i["block_num"]))
    #Check for Data Block Number errors
    max_block = superblock["num_blocks"]
    orig_block_bitmap = free_blocks
    my_block_bitmap = []
    for inode in inode_summaries:
        if(inode["mode"] == 0):
            continue
        for j in range(len(inode["blocks"])):
            if(j>14):
                break
            i = inode["blocks"][j]
            offset, s = calculate_offset(j)
            if(i!=0):
                if( (i < 0) or i>max_block):
                    print("INVALID "+ s + "BLOCK " + str(i) + " IN INODE " + str(inode["number"]) + " AT OFFSET " + str(offset))
                elif(i in reserved):
                    print("RESERVED")
                elif(i in orig_block_bitmap):
                    print("ALLOCATED")
                elif(i in my_block_bitmap):
                    print("DUPLICATED")
                my_block_bitmap.append(i)
            

            






if __name__ == "__main__":
    main()