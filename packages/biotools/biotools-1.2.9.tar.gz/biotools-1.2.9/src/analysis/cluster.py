#!/usr/bin/env python
import biotools.sequence as sequ
import biotools.IO as io
import biotools.translate as tran
import biotools.clustal as clustal
import biotools.analysis.options as options
try:
    import Queue as queue
except ImportError:
    import queue
import hashlib
import subprocess
import threading
from os import sep, mkdir


def run(direc, inputs):
    '''
    Takes a collection of files generated by gene prediction, creates clusters
    based off of the genes that have homology to those predicted genes, and
    creates new fasta files in the clusters sub directory under the given
    directory and separated according to whether they are nucleotide or amino
    acid sequnces. These new fasta files are then used to create clustalw
    alignments of the genes if more than 1 sequence exists in the fasta file.
    '''

    clusters = {}
    all_ids = set()
    ids = {}
    q = queue.Queue()
    filenames = []

    def run_clustal():
        while not q.empty():
            cid = q.get()
            dig = hashlib.md5()
            dig.update(' '.join(cid))
            dig = dig.hexdigest()

            fpre = direc + 'nt' + sep + dig
            apre = direc + 'aa' + sep + dig
            fname = fpre + ".fasta"
            aname = apre + ".fasta"

            fh = io.open(fname, 'w')
            ah = io.open(aname, 'w')
            for ipt in clusters:
                counter = 0
                name = '_'.join(ipt.split(sep)[-1].split('.')[0].split())
                for cluster in clusters[ipt]:
                    if cid & cluster[0]:
                        nm = name + '_' + str(counter)
                        seq = cluster[1]
                        curr = sequ.Sequence(nm, seq, defline=', '.join(cid))
                        tr = tran.translate(curr)
                        tr.name = curr.name
                        fh.write(curr)
                        ah.write(tr)
                        counter += 1
            fh.close()
            ah.close()

            try:
                clustal.run(fname, fpre + '.clustalw')
                clustal.run(aname, apre + '.clustalw')
                filenames.append(dig + '.fasta')
            except ValueError:
                pass

            q.task_done()

    if direc:
        for d in [direc, direc + 'nt' + sep, direc + 'aa' + sep]:
            try:
                mkdir(d)
            except OSError:
                pass

    for ipt in inputs:
        print "loadin' up from", ipt
        seqs = {}
        ids[ipt] = set()
        for seq in io.open(ipt, 'r'):
            ids[ipt].add(seq.name)
            all_ids.add(seq.name)
            if seq.seq not in seqs:
                seqs[seq.seq] = set()
            seqs[seq.seq].add(seq.name)
        clusters[ipt] = [(seqs[k], k) for k in seqs]
        del seqs

    sub_ids = []
    print "we have this many sequences:",
    while all_ids:
        print len(all_ids)
        cid = all_ids.pop()
        subcluster = (all_ids | set([cid])) & \
            set(i for ipt in clusters for cluster in clusters[ipt]
                for i in cluster[0] if cid in cluster[0])

        for ipt in clusters:
            for cluster in clusters[ipt]:
                if cid in cluster[0]:
                    subcluster = (subcluster & cluster[0]) | \
                        (subcluster - ids[ipt])
        sub_ids.append(subcluster)
        print "%d - %d =" % (len(all_ids) + 1, len(subcluster)), 
        all_ids -= subcluster

    for cid in sub_ids:
        q.put(cid)

    threads = []
    for i in xrange(options.NUM_PROCESSES - 1):
        curr = threading.Thread(target=run_clustal)
        threads.append(curr)
        curr.start()
    run_clustal()
    q.join()
    return filenames
