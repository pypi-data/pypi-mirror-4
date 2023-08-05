class MLGN:
    def __init__(self):
        self.job_id = ''
    def predict(self, seq):
        """
        Start your prediction!

        * input:
         - seq, example: >fasta\nMKLSINKNTLESAVILCNAYVEKKDSSTITSHLFFHADEDKLLIKASDYEIGINYKIKKIRVESSGFATANAKSIADVIKSLNNEEVVLETIDNFLFVRQKNTKYK
        * output:
         - job_id, example: 9FWYP9"""
        from suds.client import Client
        #URL with WSDL file
        url = 'http://iimcb.genesilico.pl/MetaLocGramN/soap/services.wsdl'
        self.client = Client(url)
        self.job_id = self.client.service.predict(seq)
        return self.job_id
    def get_job_id(self):
        """Get your job_id

        example:
        9FWYP9"""
        return self.job_id
    def get_status(self):
        """Get a status of your job.

        example:
        primary prediction::in progress
        primary prediction::in progress
        primary prediction::in progress
        primary prediction::done
        consenus::done
        done
        """
        self.status = self.client.service.get_status(self.job_id)
        return self.status
    def get_result(self):
        """Get the result! :-)

        example:
        extracellular,47.541,0.0,0.0,0.0,52.459,
primary methods: CELLO,cytoplasmic,0.6138,0.036,0.1346,0.0612,0.1546,PSLpred,extracellular,0.2,0.531,PSORTb3,unknown,0.2,0.2,0.2,0.2,0.2,SosuiGramN,cytoplasmic

        """
        self.result =  self.client.service.get_result(self.job_id)
        return self.result

def run_example():
    """Run example!"""
    from MetaLocGramN import MLGN
    from time import sleep

    mlgn = MLGN()

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
        sleep(5)
    print mlgn.get_result()

if __name__ == "__main__":
    run_example()
