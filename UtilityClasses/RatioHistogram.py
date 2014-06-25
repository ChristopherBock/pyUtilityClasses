__author__ = 'Christopher Bock'

from LoggingClass import LoggingClass


class RatioHistogram(LoggingClass):
    """
    A convenience class to make drawing ratio histograms in ROOT (http://root.cern.ch) easier, especially when dealing
    with many histograms in the same plot at once. You can either add histograms prestyled by hand or using a styling
    function accepting one or two parameters being the histogram and optionally the name of the histogram in the legend.

    TODO:
     - add function to load histograms also from files to make life even more easy
     - check styling options inside default_options for consistency
     - add documentation to all the possible options inside default_options
    """

    def __init__(self, logger=None):
        from OptionHandler import OptionHandler

        LoggingClass.__init__(self, logger=logger)

        self.options = OptionHandler(logger)
        self.load_defaults()

        self.histograms = {}

        pass

    def load_defaults(self):
        default_options = {'batch_mode': True, 'output_file_type': 'pdf', 'safe_to_root_file': False,
                           'use_atlas_style': False, 'draw_legend': True, 'legend_text_size': 0.045,
                           'legend_x_values': [0.69, 0.86], 'legend_y_values': [0.65, 0.85], 'opt_stat': 0,
                           'draw_grid': False, 'ratio_maximum': 2.0, 'ratio_minimum': 0.5, 'ratio_xaxis_ndivisions': 306,
                           'ratio_yaxis_ndivisions': 602, 'line_width_scale': 1.5, 'override_minimum': False,
                           'override_maximum': False, 'minimum_value': 1444444, 'maximum_value': -123123,
                           'do_atlas_label': False, 'atlas_label': 'Preliminary', 'ratio_y_label': 'Ratio',
                           'omit_title': False, 'legend_automatic_columns': True, 'legend_n_columns': -1,
                           'overall_text_scale': 1.5}

        self.options.load_defaults(default_options)

        pass

    def load_options(self, file_name=''):
        if not file_name:
            pass

        self.options.parse_arguments_config_file(file_name)

        pass

    def print_settings(self):
        self.print_line()
        self.options.print_options('INFO')
        self.print_line()
        pass

    # the following convenience function still needs to be updated to work with the new code
    # def AddHistogramFromFile(self, fileName, histogramName, nameInLegend=None, directoryName=None, lineColor=-1,
    #                          markerStyle=-1, dashed=False, histogramScale=1, closeFileAfterwards=True,
    #                          closeIfOpen=True, lineStyle=None, markerSize=None, draw_option=None):
    #     '''
    #     In case no directory name has been specified, this function assumes that
    #     the complete path to the histogram is specified as histogramName
    #     Supply -1 as histogramScale to normalize histograms
    #     '''
    #     if self.batchMode:
    #         gROOT.SetBatch(True)
    #
    #     rootFile = gROOT.FindObject(fileName)
    #     if rootFile and closeIfOpen:
    #         rootFile.Close()
    #
    #     rootFile = TFile(fileName, 'READ')
    #     if not rootFile:
    #         raise NameError('Could not load root file: ' + fileName)
    #
    #     workingDirectory = rootFile
    #     if directoryName:
    #         workingDirectory = rootFile.Get(directoryName)
    #     if not workingDirectory:
    #         rootFile.Close()
    #         raise NameError('Could not open working directory: ' + directoryName)
    #
    #     temporaryHistogram = workingDirectory.Get(histogramName)
    #     if not temporaryHistogram:
    #         rootFile.Close()
    #         raise NameError('Could not load histogram: ' + histogramName)
    #     else:
    #         gROOT.cd() # needed before cloning to avoid the histogram being cleaned once we exit this function
    #         self.AddHistogram(temporaryHistogram, nameInLegend, lineColor, markerStyle, dashed, histogramScale,
    #                           lineStyle, markerSize, draw_option)
    #
    #     if closeFileAfterwards:
    #         rootFile.Close()
    #
    #     pass

    def add_histogram(self, histogram, name_in_legend=None, histogram_styler=None):
        if not histogram:
            raise AttributeError('No histogram supplied to RatioHistogram.add_histogram')

        if not name_in_legend:
            name_in_legend = histogram.GetName()

        if histogram_styler:
            import inspect
            argspec = inspect.getargspec(histogram_styler)
            if len(argspec[0]) >= 2:
                histogram_styler(histogram, name_in_legend)
            else:
                histogram_styler(histogram)

        self.histograms[name_in_legend] = histogram

        pass

    def plot(self, output_file_name, name_of_canvas='canvas', log_scale=False, ratio_log_scale=False,
             ratio_map=None, plot_ratios=True, sort_function=None):
        import ROOT

        num_histograms = len(self.histograms)

        self.print_log('Output file is named: %s and superimposes %i histograms.' % (output_file_name, num_histograms))

        if (num_histograms < 2) and plot_ratios:
            self.print_log('Need at least two histograms to create a ratio plot!', 'WARNING')
            return False

        if sort_function:
            histogram_keys = sorted(self.histograms.keys(), sort_function)
        else:
            histogram_keys = self.histograms.keys()

        ROOT.gStyle.SetOptStat(self.options['opt_stat'])

        if self.options['draw_legend']:
            legend_x_values = self.options['legend_x_values']
            legend_y_values = self.options['legend_y_values']

            legend = ROOT.TLegend(legend_x_values[0], legend_y_values[0], legend_x_values[1], legend_y_values[1])
            legend.SetBorderSize(0)
            legend.SetFillColor(0)
            legend.SetFillStyle(4050)
            legend.SetTextFont(42)
            legend.SetTextSize(legend.GetTextSize()*2)

            legend_entry_option = 'l'
            if plot_ratios:
                legend_entry_option = 'lp'

            for name in histogram_keys:
                legend.AddEntry(self.histograms[name], name, legend_entry_option)

        maximum_value = self.options['maximum_value']
        minimum_value = self.options['minimum_value']
        if not self.options['override_maximum']:
            maximum_value = -131238.
            for name, histogram in self.histograms.iteritems():
                if histogram.GetMaximum() > maximum_value:
                    maximum_value = histogram.GetMaximum()

        if not self.options['override_minimum']:
            minimum_value = 87238477.
            for name, histogram in self.histograms.iteritems():
                if histogram.GetMinimum() < minimum_value:
                        minimum_value = histogram.GetMinimum()

        ### Creating the canvas and the pads to draw the histograms and the ratio plots on ###
        canv = ROOT.TCanvas(name_of_canvas, '', 0, 0, 800, 600)
        canv.SetTicks(1, 1)

        if plot_ratios:
            y_pad_histo = 0.2
            bottom_margin_pad_histo = 0.035
            #lef_margin_pad_histo = 0.13 + self.left_margin_shift
            lef_margin_pad_histo = 0.13
        else:
            y_pad_histo = 0.0
            bottom_margin_pad_histo = 0.125
            #lef_margin_pad_histo = 0.1 + self.left_margin_shift
            lef_margin_pad_histo = 0.1

        pad_histo = ROOT.TPad('name_pad_histo', 'name_pad_histo', 0, y_pad_histo, 1., 1.)
        pad_histo.SetTicks(1, 1)
        pad_histo.SetLeftMargin(lef_margin_pad_histo)
        pad_histo.SetRightMargin(0.05)
        pad_histo.SetBottomMargin(bottom_margin_pad_histo)
        if self.options['draw_grid']:
            pad_histo.SetGrid()
        if log_scale:
            pad_histo.SetLogy(1)

        if not self.options['omit_title']:
            pad_histo.SetTopMargin(0.1)
            ROOT.gStyle.SetOptTitle(1)
        else:
            ROOT.gStyle.SetOptTitle(0)
            pad_histo.SetTopMargin(0.05)

        if plot_ratios:
            pad_ratio = ROOT.TPad('name_pad_ratio', 'name_pad_ratio', 0, 0, 1, 0.2)
            pad_ratio.SetTopMargin(0.07)
            pad_ratio.SetLeftMargin(lef_margin_pad_histo)
            pad_ratio.SetRightMargin(0.05)
            pad_ratio.SetBottomMargin(0.45)
            if self.options['draw_grid']:
                pad_ratio.SetGrid()
            if ratio_log_scale:
                pad_ratio.SetLogy(1)

            pad_ratio.Draw()  # otherwise ROOT crashes...
        pad_histo.Draw()

        ### Create the ratio histograms and draw them ###
        if plot_ratios:
            pad_ratio.cd()

            if not ratio_map:
                ratio_map = {}
                for i in range(1, num_histograms):
                    ratio_map[i] = 0

            i = 0
            ratio_histograms = []  # we need this workaround to prevent the GC from deleting the histograms too early
            for numeratorHistogram, denumeratorHistogram in ratio_map.iteritems():
                if denumeratorHistogram >= num_histograms:
                    continue
                if numeratorHistogram >= num_histograms:
                    continue

                ratio_histograms.append(self.histograms[histogram_keys[numeratorHistogram]].Clone(self.histograms[histogram_keys[numeratorHistogram]].GetName() + str(i) + 'clone'))
                hratio = ratio_histograms[i]
                hratio.Divide(self.histograms[histogram_keys[denumeratorHistogram]])

                hratio.SetTitle('')

                hratio.SetStats(0)
                hratio.SetLineColor(self.histograms[histogram_keys[numeratorHistogram]].GetLineColor())
                hratio.SetMarkerColor(self.histograms[histogram_keys[numeratorHistogram]].GetLineColor())
                hratio.SetMarkerStyle(self.histograms[histogram_keys[numeratorHistogram]].GetMarkerStyle())

                if not ratio_log_scale:
                    hratio.SetMinimum(self.options['ratio_minimum'])
                    hratio.SetMaximum(self.options['ratio_maximum'])
                else:
                    if self.options['ratio_minimum'] > 0:
                        hratio.SetMinimum(self.options['ratio_minimum'])
                    else:
                        hratio.SetMinimum(0.1)

                scalefactor = self.options['overall_text_scale'] * (1.0 - y_pad_histo) / y_pad_histo
                hratio.GetXaxis().SetLabelSize(hratio.GetXaxis().GetLabelSize() * scalefactor)
                hratio.GetYaxis().SetLabelSize(hratio.GetYaxis().GetLabelSize() * scalefactor)
                hratio.GetXaxis().SetTitleSize(hratio.GetXaxis().GetTitleSize() * scalefactor)
                hratio.GetYaxis().SetTitleSize(hratio.GetYaxis().GetTitleSize() * scalefactor)
                hratio.GetXaxis().SetTitleOffset(0.9)
                hratio.GetYaxis().SetTitleOffset(self.options['overall_text_scale']*0.9 / scalefactor)

                hratio.GetXaxis().SetNdivisions(self.options['ratio_xaxis_ndivisions'])
                hratio.GetYaxis().SetNdivisions(self.options['ratio_yaxis_ndivisions'])

                hratio.SetLineWidth(int(hratio.GetLineWidth() * self.options['line_width_scale']))

                #hratio.SetMarkerSize(hratio.GetMarkerSize()*scalefactor*0.9)

                if i > 0:
                    hratio.Draw('SAME P')
                else:
                    hratio.GetYaxis().SetTitle(self.options['ratio_y_label'])
                    hratio.Draw('P')
                    if not self.options['draw_grid']:
                        l = ROOT.TLine(hratio.GetXaxis().GetXmin(), 1, hratio.GetXaxis().GetXmax(), 1)
                        l.SetLineStyle(4)
                        l.SetLineColor(17)
                        l.Draw()
                i += 1

        ### Now draw the distributions on the main pad ##
        pad_histo.cd()

        first_key = histogram_keys[0]
        if log_scale and self.options['do_atlas_label']:
            self.histograms[first_key].SetMaximum(maximum_value * 5)
        else:
            self.histograms[first_key].SetMaximum(maximum_value * 1.15)

        if not log_scale:
            self.histograms[first_key].SetMinimum(minimum_value)

        if plot_ratios:
            x_axis_scale = 0.0
        else:
            x_axis_scale = self.options['overall_text_scale']

        self.histograms[first_key].GetXaxis().SetLabelSize(self.histograms[first_key].GetXaxis().GetLabelSize() * x_axis_scale)
        self.histograms[first_key].GetYaxis().SetLabelSize(self.histograms[first_key].GetYaxis().GetLabelSize() * self.options['overall_text_scale'])
        self.histograms[first_key].GetXaxis().SetTitleSize(self.histograms[first_key].GetXaxis().GetTitleSize() * x_axis_scale)
        self.histograms[first_key].GetYaxis().SetTitleSize(self.histograms[first_key].GetYaxis().GetTitleSize() * self.options['overall_text_scale'])

        self.histograms[first_key].GetYaxis().SetTitleOffset(0.95)

        self.histograms[first_key].SetLineWidth(int(self.histograms[first_key].GetLineWidth() * self.options['line_width_scale']))

        if not self.histograms[first_key].GetYaxis().GetTitle():
            self.histograms[first_key].GetYaxis().SetTitle('Untitled')

        self.histograms[first_key].Draw('HIST')
        for i in range(1, num_histograms):
            self.histograms[histogram_keys[i]].SetLineWidth(self.histograms[first_key].GetLineWidth())
            self.histograms[histogram_keys[i]].Draw('same HIST')

        ### Last: draw the legend ##
        legend.SetTextSize(self.options['legend_text_size'])
        if self.options['legend_automatic_columns']:
            import math
            n_columns = int(math.ceil(legend.GetNRows()/6))
            legend.SetNColumns(n_columns)
        elif self.options['legend_n_columns'] > 0:
            legend.SetNColumns(self.options['legend_n_columns'])
        legend.Draw()

        if self.options['do_atlas_label']:
            raise Exception('do_atlas_label not yet implemented!')

        canv.Print(output_file_name + '.' + self.options['output_file_type'], self.options['output_file_type'])

        return True
