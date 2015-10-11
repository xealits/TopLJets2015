import os
import sys
import optparse
from TopLJets2015.TopAnalysis.storeTools import getEOSlslist

"""
steer the script
"""
def main():

    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-i', '--inDir',       dest='inDir',       help='input directory with files',               default=None,   type='string')
    parser.add_option('-o', '--outDir',      dest='outDir',      help='output directory with files',              default=None,   type='string')
    parser.add_option('-c', '--cleanup',     dest='cleanup',     help='removes original crab directory',          default =False, action='store_true')
    parser.add_option(      '--nocheck',     dest='nocheck',     help='do not prompt user',                       default=False,  action='store_true')
    (opt, args) = parser.parse_args()

    if opt.outDir is None: opt.outDir=opt.inDir

    dset_list=getEOSlslist(directory=opt.inDir,prepend='')
    for dset in dset_list:
        dsetname=dset.split('/')[-1]

        pub_list=getEOSlslist(directory=dset,prepend='')
        for pub in pub_list:
            if not 'crab' in pub_list[0]:
                print 'Ambiguity found @ <publication-name> for <primary-dataset>=%s , bailing out'%dsetname
                continue
            pub=pub.split('/crab_')[-1]

            time_list=getEOSlslist(directory=pub_list[0],prepend='')
            if len(time_list)!=1:
                print 'Ambiguity found @ <time-stamp> for <primary-dataset>=%s , bailing out'%dsetname
                continue
            time_stamp=time_list[0].split('/')[-1]

            out_list=[]
            count_list=getEOSlslist(directory=time_list[0],prepend='')
            for count in count_list: out_list += getEOSlslist(directory=count,prepend='')
            file_list=[x for x in out_list if '.root' in x]

            newDir='%s/%s' % (opt.outDir,pub)        
            print '<primary-dataset>=%s <publication-name>=crab_%s <time-stamp>=%s has %d files' % (dsetname,pub,time_stamp,len(file_list) )
            if not opt.nocheck:
                choice = raw_input('Will move to %s current output directory. [y/n] ?' % newDir ).lower()
                if not 'y' in choice : continue
            os.system('cmsMkdir %s' % newDir)

            moveIndividualFiles=True
            if len(file_list)>0:
                subgroupMerge = int( raw_input('This set has %d files. Merge into groups? (enter 0 if no merging)' % len(file_list)) )
                if subgroupMerge>0:
                    moveIndividualFiles=False

                    splitFunc = lambda A, n=subgroupMerge: [A[i:i+n] for i in range(0, len(A), n)]
                    split_file_lists = splitFunc( file_list )
                
                    for ilist in xrange(0,len(split_file_lists)):
                        mergedFileName='/tmp/MergedMiniEvents_%d.root '%ilist
                        toAdd='%s ' % mergedFileName
                        for f in split_file_lists[ilist]:
                            os.system('cmsStage -f %s /tmp/' % f)
                            toAdd += '/tmp/'+os.path.basename(f) + ' '
                        
                        os.system('hadd -f %s'%toAdd)
                        os.system('cmsStage -f %s %s/' %(mergedFileName,newDir))
                        os.system('rm %s' % toAdd)

                #if still needed copy individual files
                if moveIndividualFiles:
                    for f in file_list : os.system('cmsStage -f %s %s/' % (f, newDir) )

            if not opt.nocheck and opt.cleanup : 
                choice = raw_input('Will remove output directory. [y/n] ?').lower()
                if 'y' in choice: os.system('cmsRm -r %s' % dset)

            print 'Crab outputs may now be found in %s' % newDir

    print '-'*50
    print 'All done. In case errors were found check that the crab output structure is '
    print '<outLFNDirBase>/<primary-dataset>/<publication-name>/<time-stamp>/<counter>/<file-name>'
    print '-'*50
        


"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())
