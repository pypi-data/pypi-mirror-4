import MetaLocGramN
import time

if __name__ == "__main__":
    mlgn = MetaLocGramN.MLGN()

    seq = """>fasta
    MKLSINKNTLESAVILCNAYVEKKDSSTITSHLFFHADEDKLLIKASDYEIGI
    NYKIKKIRVESSGFATANAKSIADVIKSLNNEEVVLETIDNFLFVRQKNTKYK
    """
    mlgn.predict(seq)
    print '# job_id:', mlgn.get_job_id()
    status = ''
    while True:
        status = mlgn.get_status()
        print '# status:', status
        if status == 'done':
            break
        time.sleep(5)
    print mlgn.get_result()
