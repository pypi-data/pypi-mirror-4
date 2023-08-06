import combivep.settings as combivep_settings
from combivep.cfg import Configure
from combivep.preproc.reader import UcscReader
from combivep.preproc.reader import LjbReader


class Referer(Configure):
    """To connect to reference database"""


    def __init__(self):
        Configure.__init__(self)

    def load_config(self):
        Configure.load_config(self)
        self.__ucsc_reader = UcscReader()
        self.__ucsc_reader.read(self.config_values[combivep_settings.LATEST_UCSC_FILE_NAME])
        self.__ljb_reader = LjbReader()
        self.__ljb_reader.read(self.config_values[combivep_settings.LATEST_LJB_FILE_PREFIX] + '.txt.gz')

    def validate_snp(self, chrom, pos, ref, alt):
        """

        This function checks if a given snp is valid by referencing
        with UCSC database

        The inputs of this function are in string format except "pos", which is integer.
        "chrom" can be either in format "chr1" or "1"
        "pos" is 1-based index

        return True if the snp is presented in UCSC reference database
        and False otherwise.

        """
        for rec in self.__ucsc_reader.fetch_array_snps(chrom, int(pos)-1, int(pos)):
            if rec[combivep_settings.UCSC_0_INDEX_REF] != ref:
                continue
            if ref == alt:
                continue
            ucsc_alts = rec[combivep_settings.UCSC_0_INDEX_OBSERVED].split('/')
            for ucsc_alt in ucsc_alts:
                if ucsc_alt == alt:
                    return True
        return False

    def get_scores(self, chrom, pos, ref, alt):
        """

        This function returns precomputed prediction scores from LJB database

        The inputs of this function are in string format except "pos", which is integer.
        "chrom" can be either in format "chr1" or "1"
        "pos" is 1-based index

        return hash scores if the snp is precomputed and None otherwise

        """
        return self.__ljb_reader.get_scores(chrom, pos, ref, alt)










