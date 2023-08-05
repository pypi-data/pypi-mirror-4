def read_xls(filepath):
	"""Inserts xls file content into grid"""

	import xlrd
	
	workbook = xlrd.open_workbook(filepath)
	for sheet_no, sheet in enumerate(workbook.sheets()):
		for row in xrange(sheet.nrows):
			for col in xrange(sheet.ncols):
				S[row, col, sheet_no] = \
					repr(sheet.cell(row, col).value)

	return filepath
