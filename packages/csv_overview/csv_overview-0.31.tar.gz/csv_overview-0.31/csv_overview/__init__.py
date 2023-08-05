import csv, pprint, sys, os, random

distexplore_enabled = False
try:
	import distexplore
	distexplore_enabled = True
except:
	pass

def process(path):
	f = open(path, 'rb')
	filename = os.path.basename(path)
	filename_pure = filename.rsplit('.',1)[0]
	print filename

	reader = csv.reader(f)

	columns = [x.strip() for x in reader.next()]
	#print 'Columns:', columns

	total = 0
	distribs = {}
	for column in columns:
		distribs[column] = {'value': {}, 'empty': 0, 'numeric': 0, 'numeric_values': []}

	for cols in reader:
		total = total + 1

		for i,col in enumerate(cols):
			distribs[columns[i]]['value'][col] = distribs[columns[i]]['value'].get(col, 0) + 1
			if col.strip() == '':
				distribs[columns[i]]['empty'] += 1
			try:
				v = float(col)
				distribs[columns[i]]['numeric'] += 1
				distribs[columns[i]]['numeric_values'].append(v)
			except ValueError:
				pass

	print '%d entries' % total
	for i,col in enumerate(columns):
		print '\t(%d) %s: %d unique (%.2f%%)\n\t\t%d empty (%.2f%%),\n\t\t%d numeric (%.2f%%)' % (
			i, col,
			len(distribs[col]['value']),
			(len(distribs[col]['value'])*100.0)/total,
			distribs[col]['empty'],
			(distribs[col]['empty']*100.0) / total,
			distribs[col]['numeric'],
			(distribs[col]['numeric']*100.0) / total
			)
		print '\t\te.g. %r' % [random.choice(distribs[col]['value'].keys()) for i in xrange(5)]

	def average(seq):
		return sum(seq)*1.0/len(seq)


	print 'Numerics:'
	for col in columns:
		if (distribs[col]['numeric']*1.0) / total > 0.7:
			print '\t%s: %f - %f (avg: %r, non-0 avg: %r, median: %f, mode: %r)' % (
				col,
				min(distribs[col]['numeric_values']),
				max(distribs[col]['numeric_values']),
				average(distribs[col]['numeric_values']),
				average([x for x in distribs[col]['numeric_values'] if x != 0]),
				distribs[col]['numeric_values'][len(distribs[col]['numeric_values'])/2],
				max(distribs[col]['value'].items(), key=lambda x: x[1])[0]
				)
			if distexplore_enabled:
				distexplore.distribution_file('distributions/%s-%s.html' % (filename_pure, col),
					col,
					distribs[col]['numeric_values'],
					circular=False, freqrep=True)
				distexplore.distribution_file('distributions/%s-%s-no0.html' % (filename_pure, col),
					col,
					[x for x in distribs[col]['numeric_values'] if x != 0],
					circular=False, freqrep=True)

	f.close()

def run(args):
	if len(args) < 2 or (len(args) >= 2 and args[1] in ['help', '-h', '--help']):
		print 'Usage:'
		print '\tcsv-overview data.csv'
	else:
		run(args[1])

if __name__ == '__main__':
	run(sys.argv)