import pysam
import combivep.settings as combivep_settings
from combivep.template import CombiVEPBase


class UcscReader(CombiVEPBase):
    """to read UCSC parsed file in tabix format"""

    def __init__(self):
        CombiVEPBase.__init__(self)

    def read(self, tabix_file):
        self.db_file_name = tabix_file

    def fetch_array_snps(self, chromosome, start_pos, end_pos):
        tabix_file = pysam.Tabixfile(self.db_file_name)
        if chromosome.startswith('chr'):
            chrom = chromosome
        else:
            chrom = 'chr' + chromosome
        for line in tabix_file.fetch(chrom, start_pos, end_pos):
            yield line.rstrip('\n').split('\t')

    def fetch_hash_snps(self, chromosome, start_pos, end_pos):
        for rec in self.fetch_array_snps(chromosome, start_pos, end_pos):
            if len(rec) != combivep_settings.UCSC_EXPECTED_LENGTH :
                raise Exception("Invalid formatting is found in file '%s'>> Chrom : %s\tStart pos : %s\tEnd pos : %s" % (self.db_file_name, rec[combivep_settings.UCSC_0_INDEX_CHROM], rec[combivep_settings.UCSC_0_INDEX_START_POS], rec[combivep_settings.UCSC_0_INDEX_END_POS]))
            snp_info = {combivep_settings.KEY_UCSC_CHROM     : rec[combivep_settings.UCSC_0_INDEX_CHROM], 
                        combivep_settings.KEY_UCSC_START_POS : rec[combivep_settings.UCSC_0_INDEX_START_POS],
                        combivep_settings.KEY_UCSC_END_POS   : rec[combivep_settings.UCSC_0_INDEX_END_POS],
                        combivep_settings.KEY_UCSC_STRAND    : rec[combivep_settings.UCSC_0_INDEX_STRAND],
                        combivep_settings.KEY_UCSC_REF       : rec[combivep_settings.UCSC_0_INDEX_REF],
                        combivep_settings.KEY_UCSC_OBSERVED  : rec[combivep_settings.UCSC_0_INDEX_OBSERVED],
                        }
            yield {combivep_settings.KEY_SNP_INFO_SECTION : snp_info}


class LjbReader(CombiVEPBase):
    """to read parsed LJB file"""


    def __init__(self):
        CombiVEPBase.__init__(self)

    def read(self, ljb_file):
        self.db_file_name = ljb_file
        self.__tabix_file = pysam.Tabixfile(ljb_file)

    def fetch_array_snps(self, chromosome, start_pos, end_pos):
        for line in self.__tabix_file.fetch(chromosome, int(start_pos)-1, int(end_pos)):
            yield line.rstrip('\n').split('\t')

    def fetch_hash_snps(self, chromosome, start_pos, end_pos):
        for rec in self.fetch_array_snps(chromosome, start_pos, end_pos):
            if len(rec) != combivep_settings.LJB_PARSED_EXPECTED_LENGTH :
                raise Exception("Invalid formatting is found in file '%s'>> Chrom : %s\tpos : %s" % (self.db_file_name, rec[combivep_settings.LJB_PARSED_0_INDEX_CHROM], rec[combivep_settings.LJB_PARSED_0_INDEX_POS]))
            snp_info = {combivep_settings.KEY_LJB_CHROM : rec[combivep_settings.LJB_PARSED_0_INDEX_CHROM],
                        combivep_settings.KEY_LJB_POS   : rec[combivep_settings.LJB_PARSED_0_INDEX_POS],
                        combivep_settings.KEY_LJB_REF   : rec[combivep_settings.LJB_PARSED_0_INDEX_REF],
                        combivep_settings.KEY_LJB_ALT   : rec[combivep_settings.LJB_PARSED_0_INDEX_ALT],
                        }
            scores   = {combivep_settings.KEY_PHYLOP_SCORE  : rec[combivep_settings.LJB_PARSED_0_INDEX_PHYLOP_SCORE],
                        combivep_settings.KEY_SIFT_SCORE    : rec[combivep_settings.LJB_PARSED_0_INDEX_SIFT_SCORE],
                        combivep_settings.KEY_PP2_SCORE     : rec[combivep_settings.LJB_PARSED_0_INDEX_PP2_SCORE],
                        combivep_settings.KEY_LRT_SCORE     : rec[combivep_settings.LJB_PARSED_0_INDEX_LRT_SCORE],
                        combivep_settings.KEY_MT_SCORE      : rec[combivep_settings.LJB_PARSED_0_INDEX_MT_SCORE],
                        combivep_settings.KEY_GERP_SCORE    : rec[combivep_settings.LJB_PARSED_0_INDEX_GERP_SCORE],
                        }
            yield {combivep_settings.KEY_SNP_INFO_SECTION : snp_info,
                   combivep_settings.KEY_SCORES_SECTION   : scores,
                   }

    def get_scores(self, chromosome, pos, ref, alt):
        for rec in self.fetch_array_snps(chromosome, pos, pos):
            if rec[combivep_settings.LJB_PARSED_0_INDEX_REF] != ref:
                continue
            if rec[combivep_settings.LJB_PARSED_0_INDEX_ALT] != alt:
                continue
            return {combivep_settings.KEY_PHYLOP_SCORE  : rec[combivep_settings.LJB_PARSED_0_INDEX_PHYLOP_SCORE],
                    combivep_settings.KEY_SIFT_SCORE    : rec[combivep_settings.LJB_PARSED_0_INDEX_SIFT_SCORE],
                    combivep_settings.KEY_PP2_SCORE     : rec[combivep_settings.LJB_PARSED_0_INDEX_PP2_SCORE],
                    combivep_settings.KEY_LRT_SCORE     : rec[combivep_settings.LJB_PARSED_0_INDEX_LRT_SCORE],
                    combivep_settings.KEY_MT_SCORE      : rec[combivep_settings.LJB_PARSED_0_INDEX_MT_SCORE],
                    combivep_settings.KEY_GERP_SCORE    : rec[combivep_settings.LJB_PARSED_0_INDEX_GERP_SCORE],
                    }
        return None

class VcfReader(CombiVEPBase):
    """to read parsed VCF file"""


    def __init__(self):
        CombiVEPBase.__init__(self)

    def read(self, vcf_file):
        self.vcf_file_name = vcf_file

    def fetch_array_snps(self):
        vcf_file = open(self.vcf_file_name)
        for line in vcf_file:
            if line[0] == '#':
                continue
            yield line.rstrip('\n').split('\t')

    def fetch_hash_snps(self):
        for rec in self.fetch_array_snps():
            snp_info = {combivep_settings.KEY_VCF_CHROM : rec[combivep_settings.VCF_0_INDEX_CHROM],
                        combivep_settings.KEY_VCF_POS   : rec[combivep_settings.VCF_0_INDEX_POS],
                        combivep_settings.KEY_VCF_REF   : rec[combivep_settings.VCF_0_INDEX_REF],
                        combivep_settings.KEY_VCF_ALT   : rec[combivep_settings.VCF_0_INDEX_ALT],
                        }
            yield {combivep_settings.KEY_SNP_INFO_SECTION : snp_info}


class CbvReader(CombiVEPBase):
    """

    to read parsed SNPS file
    The format are CHROM, POS, REF, ALT, EFFECT.
    All fields are tab separated.

    """


    def __init__(self):
        CombiVEPBase.__init__(self)

    def read(self, cbv_file):
        self.cbv_file_name = cbv_file

    def fetch_array_snps(self):
        cbv_file = open(self.cbv_file_name)
        for line in cbv_file:
            if line[0] == '#':
                continue
            yield line.rstrip('\n').split('\t')

    def fetch_hash_snps(self):
        for rec in self.fetch_array_snps():
            snp_info = {combivep_settings.KEY_CBV_CHROM : rec[combivep_settings.CBV_0_INDEX_CHROM],
                        combivep_settings.KEY_CBV_POS   : rec[combivep_settings.CBV_0_INDEX_POS],
                        combivep_settings.KEY_CBV_REF   : rec[combivep_settings.CBV_0_INDEX_REF],
                        combivep_settings.KEY_CBV_ALT   : rec[combivep_settings.CBV_0_INDEX_ALT],
                        }
            prediction = {combivep_settings.KEY_CBV_TARGETS : rec[combivep_settings.CBV_0_INDEX_TARGETS]}
            yield {combivep_settings.KEY_SNP_INFO_SECTION   : snp_info,
                   combivep_settings.KEY_PREDICTION_SECTION : prediction,
                   }









