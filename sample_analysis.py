from skills_ml.job_postings.common_schema import JobPostingCollectionSample
from skills_ml.tests.utils import sample_factory
from skills_ml.job_postings.filtering import JobPostingFilterer

sample = sample_factory(JobPostingCollectionSample())
job_postings_generator = JobPostingCollectionSample()

print(len(list(sample)))

def is_edu_job(job):
	if job['onet_soc_code'][:3] in ['15-', '17-', '19-','11-']:
		return True
	else:
		return False

def is_edu_jobs(job):
	job_codes = job['occupationalCategory'].split(',')
	for codes in job_codes:
		if codes in ['43-5081.03', '15-1041.00']:
			return True
		else:
			return False


edu_jobs = JobPostingFilterer(
	job_posting_generator = job_postings_generator,
	filter_funcs = [is_edu_jobs]
	)

# from skills_ml.ontologies.onet import majorgroupname
# from collections import Counter
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib
# import seaborn as sns
# sns.set(style="darkgrid", font_scale=2)


# def plot_major_group_distribution(job_postings):
# 	c = Counter()
# 	for job in job_postings:
# 		c.update([job['onet_soc_code'][:2]])
# 	s = pd.Series(c).sort_index()
# 	s.index = s.index.map(majorgroupname)
# 	ax = s.plot.bar(figsize=(20,10), rot=90)
# 	ax.set_xlabel('soc_major_group')
# 	ax.set_ylabel('number of job posting')
# 	ax.set_title(f"total number: {s.sum()}")
# 	plt.show()
# 	return s


#plot_major_group_distribution(edu_jobs)


for key in edu_jobs:
	#print(key['onet_soc_code'])
	#print(key['occupationalCategory'])
	print(key['occupationalCategory'])
	print(key['title'])

