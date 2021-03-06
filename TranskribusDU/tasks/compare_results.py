import pickle
import os
import sys
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.getcwd()) ) )
print sys.path
import itertools
import pickle

import commands
from IPython import embed
import string
import Dodge_Tasks
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def getFilesList_baseline():
    listM = commands.getoutput('ls reports/*| grep -v chi2')
    files = string.split(listM,'\n')
    return files

_M=[('tf',500),('tf',1000),('tf',10000),('chi2',500),('chi2',1000),('mi_rr',500),('mi_rr',1000),('chi2_rr',500),('chi2_rr',1000)]
#Deprecated
def print_comparative_accuracies():

    B=[]
    C=[]

    files=getFilesList_baseline()
    for f in files:
        #print f
        tok=string.split(f,'_TEST')
        chi2fname_tok=[tok[0]+'chi2']+tok[1:]
        chi2fname = string.join(chi2fname_tok,'_TEST')
        #print(f,chi2fname)
        if os.path.exists(chi2fname):
            #print('\t FOUND')
            baselinereport=pickle.load(open(f))
            chi2report    =pickle.load(open(chi2fname))
            #print baselinereport,chi2report
            name = f.replace('reports/','')
            name = name.replace('.pickle','')
            #print name, baselinereport.fScore,chi2report.fScore
            #B.append(baselinereport.fScore)
            #C.append(chi2report.fScore)
            print name,baselinereport.fScore,chi2report.fScore
        else:
            print('Could not find the results for',f)


#Deprecated
def print_comparative_average_precision():
    #TODO Make this generic
    files=getFilesList_baseline()
    for f in files:
        #print f
        tok=string.split(f,'_TEST')
        chi2fname_tok=[tok[0]+'chi2']+tok[1:]
        chi2fname = string.join(chi2fname_tok,'_TEST')
        #print(f,chi2fname)
        if os.path.exists(chi2fname):
            #print('\t FOUND')
            baselinereport=pickle.load(open(f))
            chi2report    =pickle.load(open(chi2fname))
            #print baselinereport,chi2report
            name = f.replace('reports/','')
            name = name.replace('.pickle','')
            print(name)
            if hasattr(baselinereport,'average_precision') and hasattr(chi2report,'average_precision'):
                for tuple_baseline,tuple_chi2 in zip(baselinereport.average_precision,chi2report.average_precision):
                    print(' '*3,tuple_baseline[0],tuple_baseline[1],tuple_chi2[0],tuple_chi2[1])
            else:
                print('-- Error Could not find average precision for baseline or chi2 selection ')
            print('-'*30)
        else:
            print('Could not find the results for',f)

def tasks():
    sel_collections = ['DVD1', 'DVD4',
               'Plans_for_Grenoble2',
               'Plans_for_Grenoble3',
               'Plans_for_Grenoble4',
               'Plans_for_Grenoble5',
               'Plans_for_Grenoble7',]

    AD=list(itertools.product(sel_collections,sel_collections,))
    AD=filter(lambda x : x[0]!=x[1],AD)

    #Models
    #M=[('tf',500),('tf',1000),('tf',10000),('chi2',500),('chi2',1000),('mi_rr',500),('mi_rr',1000)]
    #M=[('tf',500),('tf',1000),('tf',10000),('chi2',500),('chi2',1000),('mi_rr',500),('mi_rr',1000),('chi2_rr',500),('chi2_rr',1000)]
    M=_M
    #Measure Accuracy, Macro Average Precision Macro F1
    ALL_PERF=[]
    for i,c in enumerate(AD):
        train,test=c[0],c[1]
        task_perf =[i,train,test]
        for feat_select,nb_feat in M:
            m_perf = read_report(train,test,feat_select,nb_feat)
            for p in m_perf:
                task_perf.append(p)
        ALL_PERF.append(task_perf)
    return ALL_PERF


def crf_tasks():
    sel_collections = ['DVD1', 'DVD4',
               'Plans_for_Grenoble2',
               'Plans_for_Grenoble3',
               'Plans_for_Grenoble5',
               'Plans_for_Grenoble7',]

    AD=list(itertools.product(sel_collections,sel_collections,))
    AD=filter(lambda x : x[0]!=x[1],AD)

    #Models
    #M=[('tf',500),('tf',1000),('tf',10000),('chi2',500),('chi2',1000),('mi_rr',500),('mi_rr',1000)]
    #M=[('tf',500),('tf',1000),('tf',10000),('chi2',500),('chi2',1000),('mi_rr',500),('mi_rr',1000),('chi2_rr',500),('chi2_rr',1000)]
    M=[('tf',500,''),('tf',1000,''),('chi2',500,''),('chi2',1000,''),('chi2_rr',500,''),('chi2_rr',1000,''),('tf',500,'crf'),('tf',500,'crf_uw'),
       ('tf',1000,'crf'),('chi2',500,'crf'),('chi2',1000,'crf'),('tf',0,'crf_c'),('tf',0,'crf_c_uw'),('chi2',500,'logit_2'),
       ('tf',0,'logit_3'),('tf',0,'logit_4'),('tf',0,'logit_5')
       ]


    #Measure Accuracy, Macro Average Precision Macro F1
    ALL_PERF=[]
    for i,c in enumerate(AD):
        train,test=c[0],c[1]
        task_perf =[i,train,test]
        for feat_select,nb_feat,mid in M:
            m_perf = read_report(train,test,feat_select,nb_feat,mid)
            for p in [m_perf[0],m_perf[2]]:
                task_perf.append(p)
        ALL_PERF.append(task_perf)

    #Compute Headers Her
    AD=list(itertools.product(M,['ACC','F1']))
    H=['id','train','test']
    for models,eval_metric in AD:
        if models[2].startswith('crf') :
            H.append(models[2]+'_'+str(models[0])+'_'+str(models[1])+':'+eval_metric )
        else:
            if models[2]=='':
                H.append('logit_'+str(models[0])+'_'+str(models[1])+':'+eval_metric )
            elif models[2].startswith('logit_'):
                H.append(models[2]+'_'+str(models[0])+'_'+str(models[1])+':'+eval_metric)
            else:
                raise Exception('Invalid ModelID')




    return ALL_PERF,H


def read_report(train,test,feat_select,nb_feat,mid='',report_dir='./reports'):
    model_name=Dodge_Tasks.get_model_name(train,feat_select,nb_feat,mid)

    repname='Train_'+model_name+'_TEST_'+test+'.pickle'

    rep_path=os.path.join(report_dir,repname)

    if os.path.exists(rep_path):
        report=pickle.load(open(rep_path))

        perf =[np.nan,np.nan,np.nan]

        perf[0]=report.fScore
        if hasattr(report,'average_precision'):
            perf[1]=np.mean(report.average_precision)


        #Recompute f1
        confmat=report.aConfusionMatrix
        #rows are groundtruth
        #col are predictions
        eps=1e-8

        Precision = np.diag(confmat)/(eps+confmat.sum(axis=0))
        Recall    = np.diag(confmat)/(eps+confmat.sum(axis=1))
        print Precision
        print Recall

        F1        = 2*Precision*Recall/(eps+Precision+Recall)
        perf[2]=np.mean(F1)
        return perf

    else:
        return [np.nan,np.nan,np.nan]


def get_headers_name():
    #AD=list(itertools.product([('tf',500),('tf',10000),('chi2',500),('chi2',1000),('mi_rr',500),('mi_rr',1000)],['ACC','MAP','F1']))
    AD=list(itertools.product(_M,['ACC','MAP','F1']))
    H=['id','train','test']
    for models,eval_metric in AD:
        H.append(str(models[0])+'_'+str(models[1])+':'+eval_metric )

    return H


def plot_diff(df_selection,ylim=[0.6,1],ylabel='Macro Average of F1'):

    df_selection.plot(kind='bar',ylim=ylim)
    ri =np.isfinite(df_selection.values.sum(axis=1))

    m=np.mean(df_selection.values[ri],axis=0)

    plt.xlabel('Task index')
    plt.ylabel(ylabel)

    plt.title('NaN Mean over Task:'+str(m))
    plt.grid(True)
    plt.show()






if __name__=='__main__':
    if len(sys.argv)>=2:
        mode =sys.argv[1]
        if mode =='chi2_acc':
            #Deprecated
            print_comparative_accuracies()
        elif mode =='chi2_avgp':
            #Deprecated
            print_comparative_average_precision()
        elif mode=='print':
            report_file=sys.argv[2]
            report=pickle.load(open(report_file))
            print(report)

        elif mode=='genreport':
            A=tasks()
            H=get_headers_name()
            df=pd.DataFrame(A,columns=H)
            f=open('/home/sclincha/Desktop/exp_dodge.csv','w')
            df.to_csv(f)
            f.close()

        elif mode=='gencrfreport':
            A,H=crf_tasks()
            df=pd.DataFrame(A,columns=H)
            #f=open('/home/sclincha/Desktop/ITER4/exp_dodge_crf_iter4.csv','w')
            f=open('iter5/exp_dodge_crf_iter5.csv','w')
            df.to_csv(f)
            f.close()


        else:
            raise ValueError('Invalid Mode')


    else:
        #A=tasks()
        #H=get_headers_name()
        #df=pd.DataFrame(A,columns=H)

        A,H=crf_tasks()
        df=pd.DataFrame(A,columns=H)

        '''
        sel_columns=['chi2_500:ACC','crf_tf_500:ACC','crf_chi2_500:ACC','crf_c_tf_0:ACC']
        df_sel = df[sel_columns]
        plot_diff(df_sel,ylim=[0.85,1.05],ylabel='Accuracy')

        sel_columns=['chi2_500:F1','crf_tf_500:F1','crf_chi2_500:F1','crf_c_tf_0:F1']
        df_sel = df[sel_columns]
        plot_diff(df_sel,ylim=[0.2,1],ylabel='Macro Average F1')
        '''

        '''
        sel_columns=['crf_tf_500:ACC','crf_uw_tf_500:ACC','crf_c_tf_0:ACC','crf_c_uw_tf_0:ACC']
        df_sel = df[sel_columns]
        plot_diff(df_sel,ylim=[0.85,1.05],ylabel='Accuracy')

        sel_columns=['crf_tf_500:F1','crf_uw_tf_500:F1','crf_c_tf_0:F1','crf_c_uw_tf_0:F1',]
        df_sel = df[sel_columns]
        plot_diff(df_sel,ylim=[0.2,1.0],ylabel='F1')
        '''

        sel_columns=['logit_chi2_500:ACC','logit_2_chi2_500:ACC','logit_3_tf_0:ACC','logit_4_tf_0:ACC','logit_5_tf_0:ACC','crf_c_tf_0:ACC']
        df_sel = df[sel_columns]
        plot_diff(df_sel,ylim=[0.95,1.02],ylabel='Accuracy')

        sel_columns=['logit_chi2_500:F1','logit_2_chi2_500:F1','logit_3_tf_0:F1','logit_4_tf_0:F1','logit_5_tf_0:F1','crf_c_tf_0:F1']
        df_sel = df[sel_columns]
        plot_diff(df_sel,ylim=[0.2,1.05],ylabel='F1')





        embed()
        print('Embed ...')
