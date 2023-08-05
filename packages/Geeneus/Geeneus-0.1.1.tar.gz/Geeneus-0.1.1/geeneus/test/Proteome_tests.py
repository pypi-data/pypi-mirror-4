import unittest
from geeneus import Proteome

class TestProteomeFunctions(unittest.TestCase):

    # Build manager object for all tests here
    def setUp(self):
        self.manager_cacheOn = Proteome.ProteinManager("alex.holehouse@gmail.com", cache=True)
        self.manager_cacheOff = Proteome.ProteinManager("alex.holehouse@gmail.com", cache=False)

    def test_get_sequence(self):
        # make sure we can pull a protein sequence

        testSeq = "maaaaaagagpemvrgqvfdvgprytnlsyigegaygmvcsaydnvnkvrvaikkispfehqtycqrtlreikillrfrheniigindiiraptieqmkdvyivqdlmetdlykllktqhlsndhicyflyqilrglkyihsanvlhrdlkpsnlllnttcdlkicdfglarvadpdhdhtgflteyvatrwyrapeimlnskgytksidiwsvgcilaemlsnrpifpgkhyldqlnhilgilgspsqedlnciinlkarnyllslphknkvpwnrlfpnadskaldlldkmltfnphkrieveqalahpyleqyydpsdepiaeapfkfdmelddlpkeklkelifeetarfqpgyrs"
        
        self.assertEqual(testSeq, self.manager_cacheOff.get_protein_sequence("NP_002736"))
        self.assertEqual(testSeq, self.manager_cacheOn.get_protein_sequence("NP_002736"))
        self.assertEqual("", self.manager_cacheOff.get_protein_sequence("SHOULDN'T WORK"))
        self.assertEqual("", self.manager_cacheOn.get_protein_sequence("SHOULDN'T WORK"))

        
    # check the pdb translation is working OK (uses eSearch)
    def test_PDB_translation(self):
        testSeq = "mahhhhhhmaksglrqdpqstaaatvlkraveldsesrypqalvcyqegidlllqvlkgtkdntkrcnlrekiskymdraenikkyldqekedgkyhkqikieenatgfsyeslfreylnetvtevwiedpyirhthqlynflrfcemlikrpckvktihlltsldegieqvqqsrglqeieeslrshgvllevqysssihdreirfnngwmikigrgldyfkkpqsrfslgycdfdlrpchettvdifhkkhtkni"
       
        self.assertEqual(testSeq, self.manager_cacheOff.get_protein_sequence("2YMB_A"))
        self.assertEqual(testSeq, self.manager_cacheOn.get_protein_sequence("2YMB_A"))
       
        print "The following PDB values are generic, so will return a list of GIs which we can't resolve"
        self.assertEqual("", self.manager_cacheOff.get_protein_sequence("2YMB"))
        self.assertEqual("", self.manager_cacheOn.get_protein_sequence("2YMB"))

    def test_get_protein_name(self):
        self.assertEqual('p21 [Homo sapiens]', self.manager_cacheOff.get_protein_name("AAB29246"))
        self.assertEqual('p21 [Homo sapiens]', self.manager_cacheOn.get_protein_name("AAB29246"))

    def test_get_raw_xml(self):
        self.assertEqual("AA", self.manager_cacheOff.get_raw_xml("AAB29246")[0]["GBSeq_moltype"])
        self.assertEqual("AA", self.manager_cacheOn.get_raw_xml("AAB29246")[0]["GBSeq_moltype"])

    def test_get_variants(self):
        self.assertEqual("100", self.manager_cacheOff.get_variants("P42685")[0]["Location"])
        self.assertEqual("100", self.manager_cacheOn.get_variants("P42685")[0]["Location"])
                
    def test_get_geneID(self):
        self.assertEqual("2444", self.manager_cacheOff.get_geneID("P42685"))
        self.assertEqual("2444", self.manager_cacheOn.get_geneID("P42685"))
    
    def test_get_protein_sequence_length(self):
        self.assertEqual(505, self.manager_cacheOff.get_protein_sequence_length("P42685"))
        self.assertEqual(505, self.manager_cacheOn.get_protein_sequence_length("P42685"))
        
    def test_get_ID_type(self):
        self.assertEqual("Swissprot", self.manager_cacheOff.get_ID_type("P42685")[1])
        self.assertEqual("Swissprot", self.manager_cacheOn.get_ID_type("P42685")[1])

    def test_run_translation(self):
        self.assertEqual("1169745", self.manager_cacheOff.run_translation("P42685"))
        self.assertEqual("1169745", self.manager_cacheOn.run_translation("P42685"))

    def test_purge(self):
        self.manager_cacheOff.purge()
        self.manager_cacheOn.purge()
        self.assertEqual(0, self.manager_cacheOff.get_size_of_datastore())
        self.assertEqual(0, self.manager_cacheOn.get_size_of_datastore())
        
if __name__ == '__main__':
    print "Please run all tests together"
