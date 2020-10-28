from datetime import datetime
import logging
import tempfile

from skills_utils.io import stream_json_file
from skills_utils.job_posting_import import JobPostingImportBase
from skills_utils.time import overlaps, quarter_to_daterange


def flatten(maybelist):
    if type(maybelist) is list:
        return ', '.join(maybelist)
    else:
        return maybelist


class SeekAusTransformer(JobPostingImportBase):
    DATE_FORMAT = '%Y.%m.%d'
    DATE_FORMAT1 = '%Y-%m-%d'

    def __init__(self, bucket_name=None, prefix=None, **kwargs):
        super(SeekAusTransformer, self).__init__(**kwargs)
        self.bucket_name = bucket_name
        self.prefix = prefix

    def _iter_postings(self, quarter):
        logging.info("Finding Virginia postings for %s", quarter)
        quarter_start, quarter_end = quarter_to_daterange(quarter)
        bucket = self.s3_conn.get_bucket(self.bucket_name)
        keylist = list(bucket.list(prefix=self.prefix, delimiter=''))
        for key in keylist:
            if key.name.endswith('.cache.json'):
                continue

            logging.info("Processing key %s", key.name)
            with tempfile.NamedTemporaryFile() as local_file:
                key.get_contents_to_file(local_file)
                local_file.seek(0)
                for posting in stream_json_file(local_file):
                    if len(posting['post_date']) == 0:
                        continue
                    listing_start = datetime.strptime(
                        posting['post_date'],
                        self.DATE_FORMAT1
                    )
                    if len(posting['last_expiry_check_date']) == 0:
                        listing_end = listing_start
                    else:
                        listing_end = datetime.strptime(
                            posting['last_expiry_check_date'],
                            self.DATE_FORMAT
                        )
                    if overlaps(
                        listing_start.date(),
                        listing_end.date(),
                        quarter_start,
                        quarter_end
                    ):
                        yield posting

    def _id(self, document):
        return document['id']

    def _transform(self, document):
        transformed = {
            "@context": "http://schema.org",
            "@type": "JobPosting",
        }
        basic_mappings = {
            'title': 'job_title',
            'description': 'job_description',
            'employmentType': 'job_type',
            'incentiveCompensation': 'salary_offered',
            'occupationalCategory': 'category',
            'skills': 'category',
            'id': 'uniq_id'
        }
        for target_key, source_key in basic_mappings.items():
            transformed[target_key] = flatten(document.get(source_key))

        if len(document['post_date']) == 0:
            transformed['post_date'] = None
        else:
            start = datetime.strptime(document['post_date'], self.DATE_FORMAT1)
            transformed['post_date'] = start.date().isoformat()
        if len(document['last_expiry_check_date']) == 0:
            transformed['last_expiry_check_date'] = None
        else:
            end = datetime.strptime(document['last_expiry_check_date'], self.DATE_FORMAT)
            transformed['last_expiry_check_date'] = end.isoformat()

        transformed['inferred_city'] = {
            '@type': 'Place',
            'address': {
                '@type': 'PostalAddress',
                'addressLocality': document['inferred_city'],
                'addressRegion': document['inferred_city'],
            }
        }
        # transformed['salary_offered'] = {
        #     '@type': 'MonetaryAmount',
        #     'minValue': document['salary_offered'],
        #     'maxValue': document['salary_offered'],
        #     'medianValue': document['salary_offered'],
        # }
        transformed['industry'] = document['category']
        #transformed['onet_soc_code'] = document['normalizedTitle']['onetCode']

        return transformed
