from cellnopt.wrapper import readSIF, get_data, plotModel, readMIDAS, makeCNOlist
import os

"""filenames = [
    'espelin.sif',
    'ExtLiver_PKN_PCB.sif',
    'feedbackREAL2.sif',
    'feedbackREAL.sif',
    'ffModel.sif',
    'LiverDREAM_PKN_Subnetwork_AddFeedback.sif',
    'LiverDREAM.sif',
    'model.sif',
    'NetworkDREAM4.sif',
    'network_opt.sif',
    'Network.sif',
    'simpleModel.sif',
    'test_PKN.sif',
    'test_Scaffold.sif',
    'ToyExtPKNMMB.sif',
    'ToyModel2BranchPKN.sif',
    'ToyModelT2.sif',
    'ToyModelMKMAnd.sif',
    'ToyModelMKMAndTesisV.sif',
    'ToyMKM.sif',
    'ToyModelMMB2.sif',
    'Toy_Model_MMB_Feedback_original.sif',
    'ToyModelPKNfeed.sif',
    'ToyModelPKN.sif',
    'ToyNCNOcutCompExpScaffold.sif',
    'Toy_PKN_MMB_Feedback.sif',
    'ToyMMB.sif',
    ]
"""

filenames = ["LiverDREAM.sif", "ToyModelMKM.sif"]


def create_html():
    f = open('test.html', 'w')
    for filename in filenames:
        outputsvg = filename.replace('.sif', '.svg')
        outputpng = filename.replace('.sif', '.png')
        f.write("<h1>%s</h1>\n" % filename)
        f.write("""<img src="%s" width="30%%">\n\n""" % outputpng)
        f.write("""<img src="%s" width="30%%">\n\n""" % outputsvg)
    f.close()


def test_plotmodel():
    for filename in filenames:
        output = filename.replace('.sif', '')
        outputpng = filename.replace('.sif', '.png')
        filename_midas = filename.replace('.sif', '.csv')
        try:
            m = readMIDAS(get_data(filename_midas))
            cnolist = makeCNOlist(m)
        except:
            cnolist=None


        print(filename)
        #plotModel(get_data(filename), output="PNG", filename=output, cnolist=cnolist)

        plotModel(get_data(filename), output="PNG", filename=output,cnolist=cnolist, remove_dot=False)
        try:
            print("Trying to create image for model %s..." % filename),
            plotModel(get_data(filename), output="PNG", filename=output,cnolist=cnolist, remove_dot=False)
            os.system("dot -Tsvg %s -o %s " % (output+'.dot', output+'.svg'))
            print("ok")
        except:
            print("failed")
            pass

        os.remove(output+'.dot')
        os.remove(output+'.svg')
        os.remove(output+'.png')


if __name__ == "__main__":
    test_plotmodel()
    #create_html()
