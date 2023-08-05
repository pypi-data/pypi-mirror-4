"""Definition of methods augmenting resources."""

import csv
# JSON is needed for Google visualization charts
# It is not needed for resources that are just Python dictionaries
from raisin.box.config import JSON
# PICKLED is only needed when the box needs to work on the Python
# representation in order to augment the box information.
# It is not needed when the JSON resource can be passed through as is
from raisin.box.config import PICKLED
from raisin.box import RESOURCES_REGISTRY
from gvizapi import gviz_api


# pylint: disable=R0903
class augment(object):
    """This is a decorator that registers methods augmenting resources.

    Use the decorator like this:

        @augment((JSON,PICKLED))
        def project_meta(context, box):

    The list of formats needed in the method are given as the formats
    parameter.

    * JSON is always needed when a resource is fetched from a remote server

    * PICKLED is needed when you need to do some calculations.

    This is how to use the information from the pickled information:

    box['description'] = [{'Species': box[PICKLED]['species']}]
    """
    # pylint: disable=C0103
    # This class is used as a decorator, so allow lower case name
    def __init__(self, formats):
        """Store the formats that need to be fetched for the method"""
        self.formats = formats

    def __call__(self, wrapped=None):
        """Register the method in the RESOURCES_REGISTRY"""
        if wrapped:
            RESOURCES_REGISTRY.append((wrapped.__name__,
                                       wrapped,
                                       self.formats, ))


def get_lines(box):
    """Get the lines out of a data table."""
    if not box[PICKLED]:
        return {}
    if not 'table_description' in box[PICKLED]:
        raise AttributeError(str(box))
    if not 'table_data' in box[PICKLED]:
        raise AttributeError(str(box))
    table = gviz_api.DataTable(box[PICKLED]['table_description'],
                               box[PICKLED]['table_data'])
    reader = csv.DictReader(table.ToCsv().split('\n'),
                            delimiter=',',
                            quotechar='"',
                            skipinitialspace=True)
    try:
        lines = reader.next()
    except StopIteration:
        lines = {}
    return lines


# pylint: disable=W0613
# Sometimes not all parameters are used, which is not a problem

# pylint: disable=C0103
@augment((PICKLED,))
def projects(context, box):
    """Augment resource."""
    lines = get_lines(box)
    title(box)
    box['description'] = lines
    box['description_type'] = 'projectlist'
    return box


@augment((PICKLED,))
def project_about(context, box):
    """Augment resource."""
    lines = get_lines(box)
    title(box)
    box['description'] = lines.get('Project Description', '')
    box['description_type'] = 'infotext'
    return box


@augment((PICKLED,))
def replicate_about(context, box):
    """Augment resource."""
    lines = get_lines(box)
    title(box)
    box['description'] = lines.get('Project Description', '')
    box['description_type'] = 'infotext'
    return box


@augment((PICKLED,))
def project_meta(context, box):
    """Augment resource."""
    lines = get_lines(box)
    title(box)
    box['description'] = [{'Species': lines.get('Species', '')}]
    box['description_type'] = 'properties'
    return box


@augment((PICKLED,))
def experiment_about(context, box):
    """Augment resource."""
    title(box)
    lines = get_lines(box)
    box['description'] = lines.get('Description', '')
    box['description_type'] = 'infotext'
    return box


@augment((PICKLED,))
def experiments(context, box):
    """Augment resource."""
    lines = get_lines(box)
    title(box)
    box['description'] = lines
    box['description_type'] = 'linklist'
    return box


@augment((JSON, PICKLED))
def project_experimentstable(context, box):
    """Augment resource."""
    if not box[PICKLED]:
        return
    column_number = len(box[PICKLED]['table_description'])
    javascript = """
   function makeExperimentLink(dataTable, rowNum){
       if (dataTable.getValue(rowNum, 0) != undefined) {
           return String.fromCharCode('60') + 'a href=\"/project/' + dataTable.getValue(rowNum, 0) + '/' + dataTable.getValue(rowNum, 1) + '/' + dataTable.getValue(rowNum, 2) + '\"' + String.fromCharCode('62') + dataTable.getValue(rowNum, 2) + String.fromCharCode('60') + '/a' + String.fromCharCode('62');
       }
       else {
           return '';
       };
   }
   view.setColumns([{calc:makeExperimentLink, type:'string', label:'Experiment'},%s]);
""" % str(range(3, column_number))[1:-1]
    # e.g.
    # >>> str(range(2, 4))[1:-1]
    # '2, 3'
    box['javascript'] = javascript
    title(box)
    return box


@augment((JSON, PICKLED,))
def project_experiment_subset_start(context, box):
    """Augment resource."""
    return box


@augment((JSON, PICKLED,))
def project_experiment_subset_selection(context, box):
    """Augment resource."""
    javascript = """
   function makeExperimentSubsetLink(dataTable, rowNum){
       if (dataTable.getValue(rowNum, 0) != undefined) {
           return String.fromCharCode('60') + 'a href=\"/project/' + dataTable.getValue(rowNum, 0) + '/experiment/subset/' + dataTable.getValue(rowNum, 1) + '/' + dataTable.getValue(rowNum, 2) + '\"' + String.fromCharCode('62') + dataTable.getValue(rowNum, 4) + String.fromCharCode('60') + '/a' + String.fromCharCode('62');
       }
       else {
           return '';
       };
   }
   view.setColumns([3, {calc:makeExperimentSubsetLink, type:'string', label:'Parameter Value'}, 5]);
"""
    box['javascript'] = javascript
    return box


@augment((JSON, PICKLED))
def project_experiment_subset(context, box):
    """Augment resource."""
    column_number = len(box[PICKLED]['table_description'])
    javascript = """
   function makeExperimentLink(dataTable, rowNum){
       if (dataTable.getValue(rowNum, 0) != undefined) {
           return String.fromCharCode('60') + 'a href=\"/project/' + dataTable.getValue(rowNum, 0) + '/' + dataTable.getValue(rowNum, 1) + '/' + dataTable.getValue(rowNum, 2) + '\"' + String.fromCharCode('62') + dataTable.getValue(rowNum, 2) + String.fromCharCode('60') + '/a' + String.fromCharCode('62');
       }
       else {
           return '';
       };
   }
   view.setColumns([{calc:makeExperimentLink, type:'string', label:'Experiment'},%s]);
""" % str(range(3, column_number))[1:-1]
    # e.g.
    # >>> str(range(2, 4))[1:-1]
    # '2, 3'
    box['javascript'] = javascript
    return box


@augment((JSON, PICKLED,))
def project_experiment_subset_pending(context, box):
    """Augment resource."""
    return box


@augment((JSON,))
def project_downloads(context, box):
    """Augment resource."""
    javascript = """
   function makeDownloadLink(dataTable, rowNum){
       if (dataTable.getValue(rowNum, 0) != undefined) {
           return String.fromCharCode('60') + 'a href=\"' + dataTable.getValue(rowNum, 3) + '\"' + String.fromCharCode('62') + dataTable.getValue(rowNum, 0) + String.fromCharCode('60') + '/a' + String.fromCharCode('62');
       }
       else {
           return '';
       };
   }
   view.setColumns([1,2,{calc:makeDownloadLink, type:'string', label:'.csv File Download Link'}]);
    """
    box['javascript'] = javascript
    title(box)
    return box


@augment((JSON,))
def rnadashboard(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def rnadashboard_results(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((PICKLED,))
def experiment_sample_info(context, box):
    """Augment resource."""
    title(box)
    return _sample_info(context, box)


@augment((PICKLED,))
def replicate_sample_info(context, box):
    """Augment resource."""
    title(box)
    return _sample_info(context, box)


def _sample_info(context, box):
    """Augment resource."""
    lines = get_lines(box)
    box['title'] = 'Sample Information'
    box['description'] = []
    if lines:
        if lines['Species']:
            info = {'Species': lines['Species']}
            box['description'].append(info)
        if lines['Cell Type']:
            info = {'Cell Type': lines['Cell Type']}
            box['description'].append(info)
        if lines['RNA Type']:
            info = {'RNA Type': lines['RNA Type']}
            box['description'].append(info)
        if lines['Localization']:
            info = {'Localization': lines['Localization']}
            box['description'].append(info)
        if lines['Bio Replicate']:
            info = {'Bio Replicate': lines['Bio Replicate']}
            box['description'].append(info)
        if lines['Date']:
            info = {'Date': lines['Date']}
            box['description'].append(info)
    box['description_type'] = 'properties'
    return box


@augment((PICKLED,))
def experiment_mapping_info(context, box):
    """Augment resource."""
    box['title'] = "Mapping Information"
    title(box)
    return _mapping_info(context, box)


@augment((PICKLED,))
def replicate_mapping_info(context, box):
    """Augment resource."""
    box['title'] = "Mapping Information"
    title(box)
    return _mapping_info(context, box)


@augment((PICKLED,))
def lane_mapping_info(context, box):
    """Augment resource."""
    box['title'] = "Mapping Information"
    title(box)
    return _mapping_info(context, box)


def _mapping_info(context, box):
    """Augment resource."""
    lines = get_lines(box)
    box['title'] = 'Mapping Information'
    box['description'] = []
    if lines:
        add = box['description'].append
        if lines.get('Read Length', ''):
            add({'Read Length': lines['Read Length']})
        if lines.get('Mismatches', ''):
            add({'Mismatches': lines['Mismatches']})
        if lines.get('Annotation Version', ''):
            add({'Annotation Version': lines['Annotation Version']})
        if lines.get('Annotation Source', ''):
            add({'Annotation Source': lines['Annotation Source']})
        if lines.get('Genome Assembly', ''):
            add({'Genome Assembly': lines['Genome Assembly']})
        if lines.get('Genome Source', ''):
            add({'Genome Source': lines['Genome Source']})
        if lines.get('Genome Gender', ''):
            add({'Genome Gender': lines['Genome Gender']})
    box['description_type'] = 'properties'
    return box


@augment((JSON,))
def experiment_read_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_read_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_read_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def experiment_mapping_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_mapping_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_mapping_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def experiment_expression_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_expression_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_expression_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def experiment_splicing_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_splicing_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_splicing_summary(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON, PICKLED))
def experiment_reads_containing_ambiguous_nucleotides(context, box):
    """Augment resource."""
    return _custom_spaced_chart(context, box)


@augment((JSON, PICKLED))
def replicate_reads_containing_ambiguous_nucleotides(context, box):
    """Augment resource."""
    return _custom_spaced_chart(context, box)


@augment((JSON, PICKLED))
def experiment_reads_containing_only_unambiguous_nucleotides(context, box):
    """Augment resource."""
    return _custom_spaced_chart(context, box)


@augment((JSON, PICKLED))
def replicate_reads_containing_only_unambiguous_nucleotides(context, box):
    """Augment resource."""
    return _custom_spaced_chart(context, box)


@augment((JSON, PICKLED))
def experiment_average_percentage_of_unique_reads(context, box):
    """Augment resource."""
    return _custom_spaced_chart(context, box)


@augment((JSON, PICKLED))
def replicate_average_percentage_of_unique_reads(context, box):
    """Augment resource."""
    return _custom_spaced_chart(context, box)


@augment((JSON,))
def experiment_total_ambiguous_and_unambiguous_reads(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_total_ambiguous_and_unambiguous_reads(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_total_ambiguous_and_unambiguous_reads(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def experiment_average_and_average_unique_reads(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_average_and_average_unique_reads(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_average_and_average_unique_reads(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON, PICKLED))
def experiment_percentage_of_reads_with_ambiguous_bases(context, box):
    """Augment resource."""
    return _percentage_of_reads_with_ambiguous_bases(context, box)


@augment((JSON, PICKLED))
def replicate_percentage_of_reads_with_ambiguous_bases(context, box):
    """Augment resource."""
    return _percentage_of_reads_with_ambiguous_bases(context, box)


@augment((JSON, PICKLED))
def lane_percentage_of_reads_with_ambiguous_bases(context, box):
    """Augment resource."""
    return _percentage_of_reads_with_ambiguous_bases(context, box)


@augment((JSON, PICKLED))
def experiment_quality_score_by_position(context, box):
    """Augment resource."""
    return _position(context, box)


@augment((JSON, PICKLED))
def replicate_quality_score_by_position(context, box):
    """Augment resource."""
    return _position(context, box)


@augment((JSON, PICKLED))
def lane_quality_score_by_position(context, box):
    """Augment resource."""
    return _position(context, box)


@augment((JSON, PICKLED))
def experiment_ambiguous_bases_per_position(context, box):
    """Augment resource."""
    return _position(context, box)


@augment((JSON, PICKLED))
def replicate_ambiguous_bases_per_position(context, box):
    """Augment resource."""
    return _position(context, box)


@augment((JSON, PICKLED))
def lane_ambiguous_bases_per_position(context, box):
    """Augment resource."""
    return _position(context, box)


@augment((JSON, PICKLED))
def experiment_read_distribution(self, box):
    """Experiment level read distribution"""
    return _read_distribution(self, box, 'experiment')


@augment((JSON, PICKLED))
def replicate_read_distribution(self, box):
    """Read level read distribution"""
    return _read_distribution(self, box, 'replicate')


@augment((JSON, PICKLED))
def lane_read_distribution(self, box):
    """
    The sparklines need to be inserted into the HTML table cells of the read distribution table.

    For each lane, the read distributions for the different length categories are shown.

    There is a div with a specific target id for each Google Charts Data View on the Google Charts
    Data Table.

    This is the target div for the overall distribution of the first lane:

    <div id="read_distribution_0_0_div">

    This is the target div for the overall distribution of the second lane:

    <div id="read_distribution_1_0_div">

    This is the target div for the second range (100-999):

    <div id="read_distribution_1_2_div">
    """
    return _read_distribution(self, box, 'lane')


def _read_distribution(self, box, level):
    """
    The sparklines need to be inserted into the HTML table cells of the read distribution table.

    For each lane, the read distributions for the different length categories are shown.

    There is a div with a specific target id for each Google Charts Data View on the Google Charts
    Data Table.

    This is the target div for the overall distribution of the first lane:

    <div id="read_distribution_0_0_div">

    This is the target div for the overall distribution of the second lane:

    <div id="read_distribution_1_0_div">

    This is the target div for the second range (100-999):

    <div id="read_distribution_1_2_div">
    """
    box['javascript'] = ""

    # Need to extract some infos from the table, so load the pickled dictionary
    table = box[PICKLED]

    # Fetch the lane names from the table
    table_data_items = [(item[0], item[1]) for item in table['table_data']]
    replicate_lane_names = list(set(table_data_items))
    replicate_lane_names.sort()

    # Fetch the starts from the table
    starts = list(set([item[2] for item in table['table_data']]))
    starts.sort()

    # Calculate the ranges given the starts
    ranges = {}
    for pos in range(0, len(starts)):
        if pos == len(starts) - 1:
            # The last range goes to infinity
            ranges[starts[pos]] = (str(starts[pos]), 'n')
        else:
            # The range goes until just before the start of the next range
            ranges[starts[pos]] = (str(starts[pos]), str(starts[pos + 1] - 1))

    # Dynamically fill in the table structure in the read distribution HTML
    # div element
    js = ""
    # pylint: disable=C0301
    js += """document.getElementById('%s_read_distribution_div').innerHTML='""" % level
    js += """<table class="google-visualization-table-table"><tr class="google-visualization-table-tr-head"><td class="google-visualization-table-th">Distribution</td><td class="google-visualization-table-th">Replicate / Lane</td>"""

    # Ignore the first start (0), which is reserved for the overall read distribution
    for start in starts[1:]:
        js += """<td class="google-visualization-table-th">%s - %s</td>""" % (ranges[start][0], ranges[start][1])
    js += """</tr>"""
    # Fill in the rows for each labe
    for replicate_name, lane_name in replicate_lane_names:
        js += """<tr class="google-visualization-table-tr-even"><td class="google-visualization-table-td"><div id="read_distribution_%s_0_div"></div></td><td class="google-visualization-table-td">%s / %s</td>""" % (replicate_lane_names.index((replicate_name, lane_name)), replicate_name, lane_name)
        # Fill in the cells for the individual read distributions
        for start in starts[1:]:
            js += '<td class="google-visualization-table-td">'
            js += """<div id="read_distribution_%s_%s_div"></div>""" % (replicate_lane_names.index((replicate_name, lane_name)), starts.index(start))
            js += '</td>'
        js += '</tr>'
    js += """</table>'"""
    box['javascript'] = js

    # Create the JavaScript code for the div tags that were just dynamically
    # added
    for replicate_name, lane_name in replicate_lane_names:
        for start in starts:
            # Add a new view for each range of each lane
            box['javascript'] = box['javascript'] + """
var view = new google.visualization.DataView(data);
view.setRows(data.getFilteredRows([{column: 0, value: '%s'}, {column: 1, value: '%s'}, {column: 2, value: %s}]))
view.setColumns([4])
var chart = new google.visualization.ImageSparkLine(document.getElementById('read_distribution_%s_%s_div'));
chart.draw(view, {width: 100, height: 62, showAxisLines: false,  showValueLabels: false, labelPosition: 'none'});
""" % (replicate_name,
       # Filter on replicate in the data table
       lane_name,
       # Filter on lane in the data table
       start,
       # Filter on start in the data table
       replicate_lane_names.index((replicate_name, lane_name)),
       # The index of the replicate and lane is used for target div id
       starts.index(start))
       # The index of the range is also used for the target div id

    title(box)
    return box


@augment((JSON, PICKLED))
def experiment_merged_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def replicate_merged_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def lane_merged_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def experiment_genome_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def replicate_genome_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def lane_genome_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def experiment_junction_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def replicate_junction_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def lane_junction_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def experiment_split_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def replicate_split_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def lane_split_mapped_reads(context, box):
    """Augment resource."""
    return _mapped_reads(context, box)


@augment((JSON, PICKLED))
def experiment_detected_genes(context, box):
    """Augment resource."""
    return _detected_genes(context, box)


@augment((JSON, PICKLED))
def replicate_detected_genes(context, box):
    """Augment resource."""
    return _detected_genes(context, box)


@augment((JSON, PICKLED))
def lane_detected_genes(context, box):
    """Augment resource."""
    return _detected_genes(context, box)


@augment((JSON,))
def experiment_gene_expression_profile(context, box):
    """Augment resource."""
    return _gene_expression_profile(context, box)


@augment((JSON,))
def replicate_gene_expression_profile(context, box):
    """Augment resource."""
    return _gene_expression_profile(context, box)


@augment((JSON,))
def lane_gene_expression_profile(context, box):
    """Augment resource."""
    return _gene_expression_profile(context, box)


@augment((JSON,))
def experiment_gene_expression_levels(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_gene_expression_levels(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_gene_expression_levels(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON, PICKLED))
def experiment_top_genes(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON, PICKLED))
def replicate_top_genes(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON, PICKLED))
def lane_top_genes(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON, PICKLED))
def experiment_top_transcripts(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON, PICKLED))
def replicate_top_transcripts(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON, PICKLED))
def lane_top_transcripts(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON, PICKLED))
def experiment_top_exons(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON, PICKLED))
def replicate_top_exons(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON, PICKLED))
def lane_top_exons(context, box):
    """Augment resource."""
    title(box)
    return _thousands_formatter(context, box)


@augment((JSON,))
def experiment_exon_inclusion_profile(context, box):
    """Augment resource."""
    return _exon_inclusion_profile(context, box)


@augment((JSON,))
def replicate_exon_inclusion_profile(context, box):
    """Augment resource."""
    return _exon_inclusion_profile(context, box)


@augment((JSON,))
def lane_exon_inclusion_profile(context, box):
    """Augment resource."""
    return _exon_inclusion_profile(context, box)


@augment((JSON,))
def experiment_reads_supporting_exon_inclusions(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_reads_supporting_exon_inclusions(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_reads_supporting_exon_inclusions(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def experiment_novel_junctions_from_annotated_exons(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_novel_junctions_from_annotated_exons(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_novel_junctions_from_annotated_exons(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def experiment_novel_junctions_from_unannotated_exons(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def replicate_novel_junctions_from_unannotated_exons(context, box):
    """Augment resource."""
    title(box)
    return box


@augment((JSON,))
def lane_novel_junctions_from_unannotated_exons(context, box):
    """Augment resource."""
    title(box)
    return box


def _exon_inclusion_profile(context, box):
    """Augment resource."""
    golden(box, 900)
    font_size(box)
    title(box)
    top_legend(box)
    option = "{left:'20%', right:'10%', width:'70%', height:'62%'}"
    box['chartoptions']['chartArea'] = option
    option = "{minValue:'0'}"
    box['chartoptions']['hAxis'] = option
    option = "{minValue:'0', logScale:true}"
    box['chartoptions']['vAxis'] = option
    return box


def _gene_expression_profile(context, box):
    """Augment resource."""
    area = '''{left:"10%",right:"30%",width:"60%"}'''
    box['chartoptions']['chartArea'] = area
    golden(box, 900)
    font_size(box)
    title(box)
    top_legend(box)
    option = "{left:'20%', right:'10%', width:'70%', height:'62%'}"
    box['chartoptions']['chartArea'] = option
    option = "{minValue:'0', logScale:true}"
    box['chartoptions']['hAxis'] = option
    option = "{minValue:'0', logScale:true}"
    box['chartoptions']['vAxis'] = option
    return box


def _custom_spaced_chart(context, box):
    """Augment resource."""
    box['chartoptions']['hAxis'] = '''{minValue:'0', maxValue:'100'}'''
    golden(box, 900)
    font_size(box)
    title(box)
    no_legend(box)
    option = "{left:'20%', right:'10%', width:'70%', height:'62%'}"
    box['chartoptions']['chartArea'] = option


def _thousands_formatter(context, box):
    """Augment resource."""
    javascript = "thousandsformatter.format(data, %s);\n"
    table = box[PICKLED]
    index = 0
    column_types = [desc[1] for desc in table['table_description']]
    for column_type in column_types:
        if column_type == 'number':
            box['javascript'] += javascript % index
        index += 1
    return box


def _detected_genes(context, box):
    """Augment resource."""
    box['javascript'] = ""
    table = box[PICKLED]
    # Add formatting for expression values of lanes
    for index in range(1, len(table['table_description'])):
        formatter = """thousandsformatter.format(data, %s);\n""" % index
        box['javascript'] += formatter
    title(box)
    return box


def _mapped_reads(context, box):
    """Augment resource."""
    option = '{minValue:0}'
    box['chartoptions']['hAxis'] = option
    golden(box, 900)
    font_size(box)
    title(box)
    option = "{left:'20%', right:'20%', width:'60%', height:'62%'}"
    box['chartoptions']['chartArea'] = option
    option = "{minValue:'0'}"
    box['chartoptions']['hAxis'] = option
    option = "{minValue:'0'}"
    box['chartoptions']['vAxis'] = option


def _percentage_of_reads_with_ambiguous_bases(context, box):
    """Augment resource."""
    table = box[PICKLED]
    height = max(len(table['table_data']) * 60, 160)
    box['chartoptions']['height'] = str(height)
    title(box)
    return box


def _position(context, box):
    """Augment resource."""
    golden(box, 900)
    font_size(box)
    title(box)
    top_legend(box)
    option = "{left:'20%', right:'10%', width:'70%', height:'62%'}"
    box['chartoptions']['chartArea'] = option
    option = "{minValue:'0'}"
    box['chartoptions']['hAxis'] = option
    option = "{minValue:'0', logScale:true}"
    box['chartoptions']['vAxis'] = option


def golden(box, width):
    """Use the golden ratio"""
    box['chartoptions']['width'] = str(width)
    GOLDEN = 1.61803399
    height = float(width) / GOLDEN
    box['chartoptions']['height'] = str(int(height))


def font_size(box):
    """Use the golden ratio"""
    if int(box['chartoptions']['width']) == 900:
        box['chartoptions']['fontSize'] = str(20)
    else:
        box['chartoptions']['fontSize'] = str(14)


def title(box):
    """set title safely"""
    if not 'chartoptions' in box:
        box['chartoptions'] = {}
    box['chartoptions']['title'] = box.get('title', '')


def no_legend(box):
    """Make chart option settings to make the legend disappear"""
    box['chartoptions']['legend'] = "{position:'none'}"


def top_legend(box):
    """Make chart option settings to make the legend appear on top"""
    box['chartoptions']['legend'] = "{position:'top'}"
