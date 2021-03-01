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
            superblock["num_blocks"] =  i[1] #Total number of blocks
            superblock["num_inodes"] =  i[2] #Total number of inodes
            superblock["block_size"] = i[3]
            superblock["inode_size"] =  i[4]
            superblock["blocks_per_group"] = i[5] #Maximum value, real might be less
            superblock["i_nodes per group"] = i[6] #Maximum value, real might be less
            superblock["first_inode"] = i[7]
        elif(i[0] == "GROUP"):
            group["number"] = i[1]
            group["num_blocks"] = i[2]
            group["num_inodes"] = i[3]
            group["free_blocks"] = i[4]
            group["free_inodes"] = i[5]
            group["block_bitmap"] = i[6]
            group["inode_bitmap"] = i[7]
            group["inode_table"] = i[8]
        elif(i[0] == "INODE"):
            inode = {}
            inode["number"] = i[1]
            inode["type"] = i[2]
            inode["mode"] = i[3]
            inode["owner"] = i[4]
            inode["group"] = i[5]
            inode["link_count"] = i[6]
            inode["last_change"] = i[7] 
            inode["modification"] = i[8]
            inode["last_access"] = i[9]
            inode["file_size"] = i[10]
            inode["num_blocks"] = i[11]
            inode["blocks"] = i[12:]
            inode_summaries.append(inode)
        elif(i[0] == "DIRENT"):
            dirent = {}
            dirent["parent"] = i[1]
            dirent["offset"] = i[2]
            dirent["inumber"] = i[3]
            dirent["entry_len"] = i[4]
            dirent["name_len"] = i[5]
            dirent["name"] = i[6]
            dir_entries.append(dirent)
        elif(i[0] == "INDIRECT"):
            indir = {}
            indir["inumber"] = i[1]
            indir["level"] = i[2]
            indir["offset"] = i[3]
            indir["indir"] = i[4]
            indir["block_num"] = i[5]
            indirect.append(indir)
    return free_inodes, free_blocks, superblock, group, inode_summaries, dir_entries, indirect

def main():
    free_inodes, free_blocks, superblock, group, inode_summaries, dir_entries, indirect = parse('P3B-test_1.csv')
    for i in indirect:
        print("Indirect block with block number" + str(i["block_num"]))


if __name__ == "__main__":
    main()