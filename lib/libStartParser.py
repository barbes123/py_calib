from libLists import list_of_sources as list_of_sources

def ParseInput(parser):

    dom1 = 1
    dom2 = 4
    server = 9
    runnbr = 63
    det_type = 0
    bg = 0
    grType = 'jpg'
    prefix = 'sum_fold_1'
    runnbr = -1
    simRuns = {}
    blFit = True
    blFitRes = True
    fitFunc = 'deb'
    dpi = 100
    cloverName = "Clover"


    parser.add_argument("-s", "--server", dest="server", default=server, type=int, choices=range(10),
                            help="DAQ ELIADE server, default = {}".format(server))
    parser.add_argument("-r", "--run", type=int,
                        dest="runnbr", default=runnbr,
                        help="Run number, default = {}".format(runnbr))
    parser.add_argument("-folds", "--folds",  nargs=2,
                        dest="dom", default=[dom1, dom2],
                        help="from domain, default = {} {}".format(dom1, dom2))
    parser.add_argument("-t", "--type",
                        dest="det_type", default=det_type,  type=int,
                        help="type of detector to be calibrated; default = 0".format(det_type))
    parser.add_argument('--bg', action='store_true', help="Enables all background lines")
    parser.add_argument('-K40', action='store_true', help="Enables 1460.820 keV")
    parser.add_argument('-anni', action='store_true', help="Enables 511.006 keV")
    parser.add_argument('-Tl208', action='store_true', help="Enables 2614.510 keV")
    parser.add_argument("-gr", "--graphic type: eps, jpg or none ",
                        dest="grType", default=grType, type=str, choices=('eps', 'jpeg', 'jpg', 'png', 'svg', 'svgz', 'tif', 'tiff', 'webp','none'),
                        # eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
                        help="Available graphic output: eps, jpeg, jpg, png, svg, svgz, tif, tiff, webp or none (no graphs); default = {}".format(grType))
    parser.add_argument("-prefix", "--prefix to the files to be analyzed",
                        dest="prefix", default=grType, type=str,
                        help="Prefix for matrix (TH2) to be analyzed mDelila_raw or mDelila or ...".format(prefix))
    parser.add_argument("-dpi", "--dpi",
                        dest="dpi", default=dpi, type=int,
                        help="resolution for figures; default = 100".format(dpi))
#Merging
    for el in list_of_sources:
        parser.add_argument('-{}'.format(el), '--data{}'.format(el), nargs='+',
                            help='Data for {} server run vol'.format(el))

        # parser.add_argument("-folds", "--plotFolds",
        #                     dest="plotFolds", default=0, type=str,
        #                     help="Folds to be plotted, default {} - all".format(0))

    parser.add_argument("-folds", "--plotFolds",
                        dest="plotFolds", default=[3], type=int, nargs='+',
                        help="Folds to be plotted, default is all (0), can provide a list like 1 2 3, mind that fold1 corresponds to 0")

    parser.add_argument("-sim", "--runs from simul", type=int, nargs='+',
                        dest="simRuns", default=[],
                        help="Run number from simul, default is empty")

    parser.add_argument("-gr", "--graphic type: eps, jpg or none ",
                        dest="grType", default=grType, type=str,
                        choices=('eps', 'jpeg', 'jpg', 'png', 'svg', 'svgz', 'tif', 'tiff', 'webp', 'none'),
                        # eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
                        help="Available graphic output: eps, jpeg, jpg, png, svg, svgz, tif, tiff, webp or none (no graphs); default = {}".format(
                            grType))

    parser.add_argument("-prefix", "--prefix to the files to be analyzed",
                        dest="prefix", default=grType, type=str,
                        help="Prefix for matrix (TH2) to be analyzed mDelila_raw or mDelila or ...".format(prefix))

    parser.add_argument("-name", "--name of the clover to appear on plots",
                        dest="cloverName", default=cloverName, type=str,
                        help="Name of the clover how it appears on plots")

    # parser.add_argument("-sim", "--run from simul", type=int,
    #                     dest="runnbr", default=runnbr,
    #                     help="Run number from simul, default = {}".format(runnbr))

    parser.add_argument("-fit", "--fitting the efficiency",
                        dest="fitFunc", default=fitFunc, type=str,
                        choices=('deb', 'None'),
                        # eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff, webp
                        help="Available fit Debertin [deb], ...; default = {}".format(fitFunc))

    # parser.add_argument("-dpi", "--dpi", dest="dpi", default=dpi, type=int,
    #                     help="resolution for figures; default = 100".format(dpi))


    return parser.parse_args()