#!/usr/bin/python

# @desc     Tired of having to go into each sub dir to find out whether or 
#           not you did a git commit? Tire no more, just use this!
#           
# @author   Mike Pearce <mike@mikepearce.net>
# @since    18/05/2010

# Forked by Ivan Masmitjà <imasmitja@gmail.com>

# Grab some libraries
import sys
import os
import glob
import subprocess
import fnmatch
import string
import ntpath
from optparse import OptionParser

# Setup some stuff
dirname = './'
gitted  = False
svnned  = False
mini    = True

messages = ""

parser = OptionParser(description="\
Show Status is awesome. If you tell it a directory to look in, it'll scan \
through all the sub dirs looking for a .git directory. When it finds one \
it'll look to see if there are any changes and let you know. \
It can also push and pull to/from a remote location (like github.com) \
(but only if there are no changes.) \
Contact mike@mikepearce.net for any support.")
parser.add_option("-d", "--dir",
                    dest    = "dirname", 
                    action  = "store",
                    help    = "The directory to parse sub dirs from", 
                    default = os.path.abspath("./")+"/"
                    )

parser.add_option("-v", "--verbose",
                  action    = "store_true", 
                  dest      = "verbose", 
                  default   = False,
                  help      = "Show the full detail of git status"
                  )

parser.add_option("-r", "--remote",
                action      = "store", 
                dest        = "remote", 
                default     = "",
                help        = "Set the remote name (remotename:branchname)"
                )

parser.add_option("--push",
                action      = "store_true", 
                dest        = "push", 
                default     = False,
                help        = "Do a 'git push' if you've set a remote with -r it will push to there"
                )

parser.add_option("-p", "--pull",
                action      = "store_true", 
                dest        = "pull", 
                default     = False,
                help        = "Do a 'git pull' if you've set a remote with -r it will pull from there"
                )

# Now, parse the args
(options, args) = parser.parse_args()
    
#-------------------
def show_error(error="Undefined Error!"):
#-------------------
    """Writes an error to stderr"""
    sys.stderr.write(error)
    sys.exit(1)

#-------------------
def check_output(command, allowretcode):
#-------------------
    """Wrapper to subprocess.check_output to handle git misbehavior"""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output = process.communicate()
    retcode = process.poll()
    if retcode:
            if retcode != allowretcode:
                raise subprocess.CalledProcessError(retcode, command, output=output[0])
            else:
                global messages
                messages = "\n\tWarning: git status returned %d.\
                \n\tPlease run verbose mode for more information\n" %( retcode)
                return output[0]
    return output[0] 


#return last directory or filename
#-------------------
def path_leaf(path):
#-------------------
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


#search recursivly all .git folders in a path
#-------------------
def find_repos(path):
#-------------------
    path = os.path.normpath(path)
    max_depth = 5
    res = []
    for root,dirs,files in os.walk(path, topdown=True):    

        if os.path.exists(os.path.join(root, ".git")) :
            res.append (root)
            dirs[:] = [] # Don't recurse any deeper
        else:
            # chekc depth
            depth = root[len(path) + len(os.path.sep):].count(os.path.sep)
            if depth == max_depth:                
                dirs[:] = [] # Don't recurse any deeper
    return res


#-------------------
# Now, onto the main event!
#-------------------
if __name__ == "__main__":

    sys.stdout.write('Scanning sub directories of %s\n' %options.dirname)
    git_folders = find_repos(options.dirname)   
    
    # See whats here
    for project in git_folders:        

        #is there a .git file
        if os.path.exists(project):
            
            #Yay, we found one!
            gitted = True
            
            # OK, contains a .git file. Let's descend into it
            # and ask git for a status
            #out = commands.getoutput('cd '+ project + '; git status')
            out = check_output("cd \"" + project + "\" && git status ", 1)
            
            # Mini?
            if False == options.verbose:
                if -1 != out.find('nothing'):
                    result = ": No Changes"
                    
                    # Pull from the remote
                    if False != options.pull:
                        push = check_output(
                            "cd \"" + project + "\" && git pull " +
                            ' '.join(options.remote.split(":")),0
                        )
                        result = result + " (Pulled) \n" + push
                                          
                    # Push to the remote  
                    if False != options.push:
                        push = check_output(
                            "cd \"" + project + "\" && git push " +
                            ' '.join(options.remote.split(":")),0
                        )
                        result = result + " (Pushed) \n" + push
                        
                    # Write to screen
                    sys.stdout.write("[git] " + os.path.basename(project).ljust(30) + result +"\n")
                else:
                    sys.stdout.write("[git] " + os.path.basename(project).ljust(30) + ": Changes\n")
            else:
                #Print some repo details
                sys.stdout.write("\n---------------- "+ project +" -----------------\n")
                sys.stdout.write(out)
                sys.stdout.write("\n---------------- "+ project +" -----------------\n")
                
            # Come out of the dir and into the next
            #commands.getoutput('cd ../')
            #check_output("cd ..",0)                   

            
    if False == gitted:
        show_error("Error: None of those sub directories had a .git file.\n")

    print (messages)
      
    raw_input("Press Enter to Exit")
