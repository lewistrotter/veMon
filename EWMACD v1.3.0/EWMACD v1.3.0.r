############################################################################################
### Exponentially Weighted Moving Average Change Detection (EWMACD) for R
### v 1.3.0
### Author: Evan B. Brooks
### Author email: evbrooks@vt.edu

### Citation: Brooks, E.B., R.H. Wynne, V.A. Thomas, C.E. Blinn, and J.W. Coulston. 2014. 
#### On-the-fly massively multitemporal change detection using statistical quality control 
#### charts and Landsat data. IEEE Transactions on Geosciences and Remote Sensing 
#### 52(6):3316-3332. doi: dx.doi.org/10.1109/TGRS.2013.2272545

############################################################################################


## Checking for/Installing required packages
requiredPackages=c('spatial.tools','snow')
currentlyInstalledPackages=rownames(installed.packages())

for(index in 1:length(requiredPackages)){
  if(length(currentlyInstalledPackages[which(currentlyInstalledPackages==requiredPackages[index])])==0){
    install.packages(requiredPackages[index])
  }
}

#require(spatial.tools)
require(snow)
require(raster)

# ## Data Initialization (optional)
setwd('C:/Users/Lewis/PycharmProjects/orig_ewma_brooks/EWMACD v1.3.0') # Set working directory here

fileName='Sample Data - Angle Index x1000 Stack.tif' # Filename for image stack
DateInfo=read.csv('Temporal Distribution with DOY.csv') # Ancillary date information; must at minimum contain columns for Year and Julian date (DOY)
dat=brick(fileName) # Loads the image stack

names(dat)=paste('Date',DateInfo$Month,DateInfo$Day,DateInfo$Year,sep='_') # Assigns descriptive layer names based on date
NAvalue(dat)=-1 # Sets all negative values to NA

###################################################################
###### Convenience functions and objects for use with EWMACD

## Nice color bar for EWMACD plotting
EWMAcolorbar=c(colorRampPalette(c('red','orange','yellow'))(1000),NA,colorRampPalette(c('green','darkgreen'))(1000))

## Convenience function for writing EWMA rasters with descriptive date names
# Assumes that the DateInfo object includes Year, Month, and Day
write.EWMACD=function(outputBrick,fileName=paste('EWMACD_on_',fileName,sep=''),DateInfo,trainingStart,testingEnd,...){
  writeRaster(outputBrick,fileName,format='ENVI',datatype='INT2S') # Outputs the EWMACD brick to a file  
  
  Years=DateInfo$Year
  
  trims=which(Years>=trainingStart & Years<testingEnd) # Subsets DateInfo to desired training and testing periods
  DateInfo2=DateInfo[trims,] # Adds it back to the list
  Years=DateInfo2$Year
  
  ### Adding descriptive band names
  names(outputBrick)=paste("Date",DateInfo2$Year,DateInfo2$Month,DateInfo2$Day,sep="_") # Generating the descriptive names
  con=file(paste(fileName,".hdr",sep=""),'r') # Opening a .hdr file
  Infile=readLines(con) # Reading the header
  close(con)
  outnames=c(paste(names(outputBrick)[-length(names(outputBrick))],",\n",sep=""),paste(names(outputBrick)[length(names(outputBrick))],"",sep="")) # Creating a band names string
  sink(paste(fileName,".hdr",sep="")) # Overwriting header file
  writeLines(Infile[1:(grep("band names",Infile)-1)],con) # Preserving header information
  cat('band names = {',outnames,'}\n',sep='') # Adding descriptive band names
  sink()
}


###################################################################
###### EWMACD functions for use with the calc and clusterR paradigm

## Base function (pixel-level), identical to base function for rasterEngine-based HREG except that this one does not incorporate additional arguments explicitly
EWMACD.pixel.for.calc=function(myPixel){
  #   ns=nc=numberHarmonics
  #   historybound=max(which(DateInfo$Year<trainingEnd))
  #   DOYs=DateInfo$DOY
  #   Years=DateInfo$Year

  myPixel=c(myPixel) ### Ensuring vector format
  Dates=length(myPixel) ### Convenience object
  tmp=rep(-2222,Dates) ### Coded 'No data' output, fills the output as an initial value
  Beta=cbind(rep(NA,(ns+nc+1))) ### Coded other 'No data' output for the coefficients
  tmp2=-4 # Dummy value
  myPixel00=myPixel ### Backup value for myPixel
  
  ind00=c(1:Dates) ### Index list for original data
  myPixel01=myPixel[1:historybound] ### Training data
  myPixel02=myPixel[(historybound+1):Dates] ### Testing data
  
  bkgd.ind00=which(is.na(myPixel00)==F) ### Index for all non-missing data
  myPixel0=myPixel[bkgd.ind00] ### 'Present' data
  Dates00=length(myPixel0) ### Convenience object for number of dates
  bkgd.ind01=which(is.na(myPixel00)==F & ind00<=historybound) ### Index for non-missing training data
  historybound01=length(bkgd.ind01) ### Adjustment of training cutoff to reflect present data only
  
  myPixel1=myPixel00[bkgd.ind01] ### Present training data
  timedat01=DOYs[bkgd.ind01] ### Present training dates, note the implicit dependence on DOYS
  timedat1=timedat01*2*pi/365 ### Conversion of training dates only to [0,2pi]
  timedatALL=DOYs[bkgd.ind00]*2*pi/365 ### Conversion of all present dates to [0,2pi]
  
  if(length(myPixel1)>0){ ### Checking if there is data to work with...
    
    ### Harmonic regression component
    X=cbind(rep(1,length(timedat1)),sin(t(matrix(rep(c(1:ns),length(timedat1)),ncol=length(timedat1)))*timedat1),cos(t(matrix(rep(c(1:nc),length(timedat1)),ncol=length(timedat1)))*timedat1))
    XAll=cbind(rep(1,Dates00),sin(t(matrix(rep(c(1:ns),Dates00),ncol=Dates00))*timedatALL),cos(t(matrix(rep(c(1:nc),Dates00),ncol=Dates00))*timedatALL))  
    
    
    if(length(myPixel1)>(ns+nc+1) & abs(det(t(X)%*%X))>=0.001){ # Ensuring design matrix is sufficient rank and nonsingular
      Preds1=(X%*%solve(t(X)%*%X)%*%t(X)%*%cbind(c(myPixel1)))
      
      ## Block for X-bar chart anomaly filtering
      Resids1=myPixel1-Preds1 
      std=sd(Resids1)
      screen1=(abs(Resids1)>(xBarLimit1*std))+0 
      keeps=which(screen1==0)
      if(length(keeps)>(nc+ns+1))
      {Beta=solve(t(X[keeps,])%*%X[keeps,])%*%t(X[keeps,])%*%myPixel[keeps]}
    }
    
    ### EWMA component
    if(is.na(Beta[1])==F) { ### Checking for present Beta
      y0=as.numeric(myPixel0-t(XAll%*%Beta)) ### Residuals for all present data, based on training coefficients
      y01=y0[1:historybound01] ### Training residuals only
      
      y02=c() 
      if(length(y0)>length(y01)){y02=y0[(historybound01+1):length(y0)]} ### Testing residuals
      
      mu=mean(y01) ### First estimate of historical mean (should be near 0)
      histsd=sd(y01) ### First estimate of historical SD.  
      ind0=c(1:length(y0)) ### Index for residuals
      ind01=ind0[1:historybound01] ### Index for training residuals
      
      ind02=c()
      if(length(y0)>length(y01)){ind02=ind0[(historybound01+1):length(y0)]} ### Index for testing residuals
      
      ### Creating date information in linear form (days from a starting point instead of Julian days of the year)
      eaYear=c(0,(rep(365,length(c(trainingStart:(testingEnd-1))))+1*(c(trainingStart:(testingEnd-1))%%4==0))) 
      cuYear=cumsum(eaYear)
      x0=(cuYear[Years-trainingStart+1]+DOYs)[bkgd.ind00] ### Compare this to the DateMaker function we wrote
      
      ### Modifying SD estimates based on anomalous readings in the training data
      UCL0=c(rep(xBarLimit1,length(ind01)),rep(xBarLimit2,length(ind02)))*histsd ### Note that we don't want to filter out the changes in the testing data, so xBarLimit2 is much larger!
      x=x0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      y=y0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      ind=ind0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      histsd=sd(y01[which(myPixel1>lowthresh & abs(y01)<UCL0[1:historybound01])]) ### Updating the training SD estimate.  This is the all-important driver of the EWMA control limits.
      if(is.na(histsd)==1){return(tmp)
                           break}
      
      Totals=y0*0 ### Future EWMA output
      tmp2=rep(-2222,length(y)) ### Coded values for the 'present' subset of the data
      
      ewma=y[1] ### Initialize the EWMA outputs with the first present residual
      for(i in (2):length(y)){ 
        ewma=c(ewma,(ewma[(i-1)]*(1-lambda)+lambda*y[i])) ### Appending new EWMA values for all present data.
      }
      
      UCL=histsd*lambdasigs*sqrt(lambda/(2-lambda)*(1-(1-lambda)^(2*c(1:length(y))))) ### EWMA upper control limit.  This is the threshold which dictates when the chart signals a disturbance.
      
      if(rounding==TRUE){tmp2=sign(ewma)*floor(abs(ewma/UCL))} ### Integer value for EWMA output relative to control limit (rounded towards 0).  A value of +/-1 represents the weakest disturbance signal
      if(rounding==FALSE){tmp2=round(ewma,0)} ### EWMA outputs in terms of resdiual scales.  
      
      ###  Keeping only values for which a disturbance is sustained, using persistence as the threshold
      if(persistence>1 & length(tmp2)>3){ ### Ensuring sufficent data for tmp2
        tmpsign=sign(tmp2) # Disturbance direction
        shiftpoints=c(1,which(tmpsign[-1]!=tmpsign[-length(tmpsign)]),length(tmpsign)) # Dates for which direction changes
        
        tmp3=rep(0,length(tmpsign))
        for(i in 1:length(tmpsign)){  # Counting the consecutive dates in which directions are sustained
          tmp3lo=0
          tmp3hi=0
          
          while(((i-tmp3lo)>0)){if((tmpsign[i]-tmpsign[i-tmp3lo])==0){tmp3lo=tmp3lo+1} else{break}}
          while(((tmp3hi+i)<=length(tmpsign))){if((tmpsign[i+tmp3hi]-tmpsign[i])==0){tmp3hi=tmp3hi+1} else{break}}
          tmp3[i]=tmp3lo+tmp3hi-1
          
        }
        
        tmp4=rep(0, length(tmp3)) 
        for(i in 1:length(tmp3)){ # If sustained dates are long enough, keep; otherwise set to previous sustained state
          if(tmp3[i]>=persistence){tmp4[i]=tmp2[i]} else {tmp4[i]=max(tmp2[which.max(tmp3[which(tmp3[1:i]>=persistence)])],0)}
        }
        
        tmp2=tmp4
        
      }
      
      tmp[bkgd.ind00[ind]]=tmp2 ### Assigning EWMA outputs for present data to the original template.  This still leaves -2222's everywhere the data was missing or filtered.
      
      if(tmp[1]==-2222){ ### If the first date of myPixel was missing/filtered, then assign the EWMA output as 0 (no disturbance).
        tmp[1]=0
      }
      
      if(tmp[1]!=-2222){ ### If we have EWMA information for the first date, then for each missing/filtered date in the record, fill with the last known EWMA value
        for(stepper in 2:Dates){
          if(tmp[stepper]==-2222){tmp[stepper]=tmp[stepper-1]}
        }
      }
      
    }
  }
  return(as.integer(tmp)) ### Final output.  All -2222's if data were insufficient to run the algorithm, otherwise an EWMA record of relative (rounded=T) or raw-residual (rounded=F) format.
}

#EWMACD.pixel.for.calc(dat[1]) ## Testing the function


## LT MODDED - Base function (pixel-level), identical to base function for rasterEngine-based HREG except that this one does not incorporate additional arguments explicitly
EWMACD.pixel.for.calc.lt=function(myPixel, ns,nc,historybound,DOYs,xBarLimit1,trainingStart,testingEnd,Years,xBarLimit2,lowthresh,lambda,lambdasigs,rounding,persistence,trainingEnd){

  myPixel=c(myPixel) ### Ensuring vector format
  Dates=length(myPixel) ### Convenience object
  tmp=rep(-2222,Dates) ### Coded 'No data' output, fills the output as an initial value
  Beta=cbind(rep(NA,(ns+nc+1))) ### Coded other 'No data' output for the coefficients
  tmp2=-4 # Dummy value
  myPixel00=myPixel ### Backup value for myPixel

  ind00=c(1:Dates) ### Index list for original data
  myPixel01=myPixel[1:historybound] ### Training data
  myPixel02=myPixel[(historybound+1):Dates] ### Testing data

  bkgd.ind00=which(is.na(myPixel00)==F) ### Index for all non-missing data
  myPixel0=myPixel[bkgd.ind00] ### 'Present' data
  Dates00=length(myPixel0) ### Convenience object for number of dates
  bkgd.ind01=which(is.na(myPixel00)==F & ind00<=historybound) ### Index for non-missing training data
  historybound01=length(bkgd.ind01) ### Adjustment of training cutoff to reflect present data only

  myPixel1=myPixel00[bkgd.ind01] ### Present training data
  timedat01=DOYs[bkgd.ind01] ### Present training dates, note the implicit dependence on DOYS
  timedat1=timedat01*2*pi/365 ### Conversion of training dates only to [0,2pi]
  timedatALL=DOYs[bkgd.ind00]*2*pi/365 ### Conversion of all present dates to [0,2pi]

  if(length(myPixel1)>0){ ### Checking if there is data to work with...

    ### Harmonic regression component (design matrix)
    X=cbind(rep(1,length(timedat1)),sin(t(matrix(rep(c(1:ns),length(timedat1)),ncol=length(timedat1)))*timedat1),cos(t(matrix(rep(c(1:nc),length(timedat1)),ncol=length(timedat1)))*timedat1))
    XAll=cbind(rep(1,Dates00),sin(t(matrix(rep(c(1:ns),Dates00),ncol=Dates00))*timedatALL),cos(t(matrix(rep(c(1:nc),Dates00),ncol=Dates00))*timedatALL))


    if(length(myPixel1)>(ns+nc+1) & abs(det(t(X)%*%X))>=0.001){ # Ensuring design matrix is sufficient rank and nonsingular
      Preds1=(X%*%solve(t(X)%*%X)%*%t(X)%*%cbind(c(myPixel1)))  # this is least squares estimation equation

      ## Block for X-bar chart anomaly filtering
      Resids1=myPixel1-Preds1
      std=sd(Resids1)
      screen1=(abs(Resids1)>(xBarLimit1*std))+0
      keeps=which(screen1==0)
      if(length(keeps)>(nc+ns+1)) {
        Beta=solve(t(X[keeps,])%*%X[keeps,])%*%t(X[keeps,])%*%myPixel[keeps]
      }
    }

    ### EWMA component
    if(is.na(Beta[1])==F) { ### Checking for present Beta
      y0=as.numeric(myPixel0-t(XAll%*%Beta)) ### Residuals for all present data, based on training coefficients
      y01=y0[1:historybound01] ### Training residuals only

      y02=c()
      if(length(y0)>length(y01)){
        y02=y0[(historybound01+1):length(y0)]
      } ### Testing residuals

      mu=mean(y01) ### First estimate of historical mean (should be near 0)
      histsd=sd(y01) ### First estimate of historical SD.
      ind0=c(1:length(y0)) ### Index for residuals
      ind01=ind0[1:historybound01] ### Index for training residuals

      ind02=c()
      if(length(y0)>length(y01)){
        ind02=ind0[(historybound01+1):length(y0)]
      } ### Index for testing residuals

      ### Creating date information in linear form (days from a starting point instead of Julian days of the year)
      eaYear=c(0,(rep(365,length(c(trainingStart:(testingEnd-1))))+1*(c(trainingStart:(testingEnd-1))%%4==0)))
      cuYear=cumsum(eaYear)
      x0=(cuYear[Years-trainingStart+1]+DOYs)[bkgd.ind00] ### Compare this to the DateMaker function we wrote

      ### Modifying SD estimates based on anomalous readings in the training data
      UCL0=c(rep(xBarLimit1,length(ind01)),rep(xBarLimit2,length(ind02)))*histsd ### Note that we don't want to filter out the changes in the testing data, so xBarLimit2 is much larger!
      x=x0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      y=y0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      ind=ind0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      histsd=sd(y01[which(myPixel1>lowthresh & abs(y01)<UCL0[1:historybound01])]) ### Updating the training SD estimate.  This is the all-important driver of the EWMA control limits.
      if(is.na(histsd)==1){
        return(tmp)
        break
      }

      Totals=y0*0 ### Future EWMA output
      tmp2=rep(-2222,length(y)) ### Coded values for the 'present' subset of the data

      ewma=y[1] ### Initialize the EWMA outputs with the first present residual
      for(i in (2):length(y)){
        ewma=c(ewma,(ewma[(i-1)]*(1-lambda)+lambda*y[i])) ### Appending new EWMA values for all present data.
      }

      UCL=histsd*lambdasigs*sqrt(lambda/(2-lambda)*(1-(1-lambda)^(2*c(1:length(y))))) ### EWMA upper control limit.  This is the threshold which dictates when the chart signals a disturbance.

      if(rounding==TRUE){tmp2=sign(ewma)*floor(abs(ewma/UCL))} ### Integer value for EWMA output relative to control limit (rounded towards 0).  A value of +/-1 represents the weakest disturbance signal
      if(rounding==FALSE){tmp2=round(ewma,0)} ### EWMA outputs in terms of resdiual scales.

      ###  Keeping only values for which a disturbance is sustained, using persistence as the threshold
      if(persistence>1 & length(tmp2)>3){ ### Ensuring sufficent data for tmp2
        tmpsign=sign(tmp2) # Disturbance direction
        shiftpoints=c(1,which(tmpsign[-1]!=tmpsign[-length(tmpsign)]),length(tmpsign)) # Dates for which direction changes

        tmp3=rep(0,length(tmpsign))
        for(i in 1:length(tmpsign)){  # Counting the consecutive dates in which directions are sustained
          tmp3lo=0
          tmp3hi=0

          while(((i-tmp3lo)>0)){
             if((tmpsign[i]-tmpsign[i-tmp3lo])==0){
               tmp3lo=tmp3lo+1
             } else{
               break
             }
          }
          while(((tmp3hi+i)<=length(tmpsign))){
             if((tmpsign[i+tmp3hi]-tmpsign[i])==0){
               tmp3hi=tmp3hi+1
             } else{
               break
             }
          }

          tmp3[i]=tmp3lo+tmp3hi-1
        }

        tmp4=rep(0, length(tmp3))
        for(i in 1:length(tmp3)){ # If sustained dates are long enough, keep; otherwise set to previous sustained state
          if(tmp3[i]>=persistence){
            tmp4[i]=tmp2[i]
          } else {
            tmp4[i]=max(tmp2[which.max(tmp3[which(tmp3[1:i]>=persistence)])],0)
            #w_=which(tmp3[1:i]>=persistence)
            #m_=which.max(tmp3[w_])
            #v_=max(tmp2[m_],0)
            #tmp4[i]=v_
          }
        }

        tmp2=tmp4

      }

      tmp[bkgd.ind00[ind]]=tmp2 ### Assigning EWMA outputs for present data to the original template.  This still leaves -2222's everywhere the data was missing or filtered.

      if(tmp[1]==-2222){ ### If the first date of myPixel was missing/filtered, then assign the EWMA output as 0 (no disturbance).
        tmp[1]=0
      }

      if(tmp[1]!=-2222){ ### If we have EWMA information for the first date, then for each missing/filtered date in the record, fill with the last known EWMA value
        for(stepper in 2:Dates){
          if(tmp[stepper]==-2222){
            tmp[stepper]=tmp[stepper-1]
          }
        }
      }
    }
  }

  lines(tmp)

  return(as.integer(tmp)) ### Final output.  All -2222's if data were insufficient to run the algorithm, otherwise an EWMA record of relative (rounded=T) or raw-residual (rounded=F) format.
}


## Wrapper (incorporates parallel processing capability), requires 'snow'
EWMACD=function(inputBrick,DateInfo,trainingStart,trainingEnd,testingEnd,numberHarmonics=3,xBarLimit1=1.5,xBarLimit2=20,lowthresh=100,
                lambda=0.3,lambdasigs=3,rounding=T,persistence=3,numberCPUs='all',writeFile=F,fileName=paste('EWMACD_Outputs',sep=''),...){
  if(numberCPUs=='all'){
    beginCluster()
  } else {
    beginCluster(numberCPUs)
  }

  ns=nc=numberHarmonics
  DOYs=DateInfo$DOY
  Years=DateInfo$Year
  
  trims=which(Years>=trainingStart & Years<testingEnd) # Subsets DateInfo to desired training and testing periods
  DateInfo2=DateInfo[trims,] # Adds it back to the list
  DOYs=DateInfo2$DOY
  Years=DateInfo2$Year
  inputBrick=subset(inputBrick,trims)
  
  historybound=max(which(Years<trainingEnd))
  
  # cl=getCluster()
  # clusterExport(cl,c('EWMACD.pixel.for.calc','ns','nc','historybound','DOYs','xBarLimit1','trainingStart','testingEnd','Years','xBarLimit2','lowthresh','lambda','lambdasigs','rounding','persistence','trainingEnd'),envir=environment())
  # executionTime= system.time((
  #   tmpOutput=clusterR(inputBrick,fun=function(x){calc(x,EWMACD.pixel.for.calc)})
  # ))[3]
  # endCluster()

  # lewis modded
  myPixel=dat[1]
  tmpOutput=EWMACD.pixel.for.calc.lt(myPixel,ns,nc,historybound,DOYs,xBarLimit1,trainingStart,testingEnd,Years,xBarLimit2,
                                     lowthresh,lambda,lambdasigs,rounding,persistence,trainingEnd)

  #if(writeFile==T){write.EWMACD(tmpOutput,fileName,DateInfo=DateInfo2,trainingStart=trainingStart,testingEnd=testingEnd)}

  executionTime=1.5

  output=list(tmpOutput,executionTime)
  names(output)=c('EWMACD','executionTime')
  return(output)
  
}

test2a=EWMACD(inputBrick=dat,DateInfo=DateInfo,trainingStart=2005,trainingEnd=2008,testingEnd=2012,numberCPUs=1)
plot(test2a$EWMACD,51,col=EWMAcolorbar,zlim=c(-15,15))


###################################################################
###### EWMACD functions for use with the rasterEngine paradigm

## Base function (pixel-level), identical to base function for rasterEngine-based HREG except that this one does not incorporate additional arguments explicitly
EWMACD.pixel.for.rasterEngine=function(myPixel,nc,ns,DOYs,Years,historybound,xBarLimit1,xBarLimit2,lowthresh,lambdasigs,lambda,rounding,persistence,trainingStart,trainingEnd,testingEnd,...){
  myPixel=c(myPixel) ### Ensuring vector format
  Dates=length(myPixel) ### Convenience object
  tmp=rep(-2222,Dates) ### Coded 'No data' output, fills the output as an initial value
  Beta=cbind(rep(NA,(ns+nc+1))) ### Coded other 'No data' output for the coefficients
  tmp2=-4 # Dummy value
  myPixel00=myPixel ### Backup value for myPixel
  
  ind00=c(1:Dates) ### Index list for original data
  myPixel01=myPixel[1:historybound] ### Training data
  myPixel02=myPixel[(historybound+1):Dates] ### Testing data
  
  bkgd.ind00=which(is.na(myPixel00)==F) ### Index for all non-missing data
  myPixel0=myPixel[bkgd.ind00] ### 'Present' data
  Dates00=length(myPixel0) ### Convenience object for number of dates
  bkgd.ind01=which(is.na(myPixel00)==F & ind00<=historybound) ### Index for non-missing training data
  historybound01=length(bkgd.ind01) ### Adjustment of training cutoff to reflect present data only
  
  myPixel1=myPixel00[bkgd.ind01] ### Present training data
  timedat01=DOYs[bkgd.ind01] ### Present training dates, note the implicit dependence on DOYS
  timedat1=timedat01*2*pi/365 ### Conversion of training dates only to [0,2pi]
  timedatALL=DOYs[bkgd.ind00]*2*pi/365 ### Conversion of all present dates to [0,2pi]
  
  if(length(myPixel1)>0){ ### Checking if there is data to work with...
    
    ### Harmonic regression component
    X=cbind(rep(1,length(timedat1)),sin(t(matrix(rep(c(1:ns),length(timedat1)),ncol=length(timedat1)))*timedat1),cos(t(matrix(rep(c(1:nc),length(timedat1)),ncol=length(timedat1)))*timedat1))
    XAll=cbind(rep(1,Dates00),sin(t(matrix(rep(c(1:ns),Dates00),ncol=Dates00))*timedatALL),cos(t(matrix(rep(c(1:nc),Dates00),ncol=Dates00))*timedatALL))  
    
    
    if(length(myPixel1)>(ns+nc+1) & abs(det(t(X)%*%X))>=0.001){ # Ensuring design matrix is sufficient rank and nonsingular
      Preds1=(X%*%solve(t(X)%*%X)%*%t(X)%*%cbind(c(myPixel1)))
      
      ## Block for X-bar chart anomaly filtering
      Resids1=myPixel1-Preds1 
      std=sd(Resids1)
      screen1=(abs(Resids1)>(xBarLimit1*std))+0 
      keeps=which(screen1==0)
      if(length(keeps)>(nc+ns+1))
      {Beta=solve(t(X[keeps,])%*%X[keeps,])%*%t(X[keeps,])%*%myPixel[keeps]}
    }
    
    ### EWMA component
    if(is.na(Beta[1])==F) { ### Checking for present Beta
      y0=as.numeric(myPixel0-t(XAll%*%Beta)) ### Residuals for all present data, based on training coefficients
      y01=y0[1:historybound01] ### Training residuals only
      
      y02=c() 
      if(length(y0)>length(y01)){y02=y0[(historybound01+1):length(y0)]} ### Testing residuals
      
      mu=mean(y01) ### First estimate of historical mean (should be near 0)
      histsd=sd(y01) ### First estimate of historical SD.  
      ind0=c(1:length(y0)) ### Index for residuals
      ind01=ind0[1:historybound01] ### Index for training residuals
      
      ind02=c()
      if(length(y0)>length(y01)){ind02=ind0[(historybound01+1):length(y0)]} ### Index for testing residuals
      
      ### Creating date information in linear form (days from a starting point instead of Julian days of the year)
      eaYear=c(0,(rep(365,length(c(trainingStart:(testingEnd-1))))+1*(c(trainingStart:(testingEnd-1))%%4==0))) 
      cuYear=cumsum(eaYear)
      x0=(cuYear[Years-trainingStart+1]+DOYs)[bkgd.ind00] ### Compare this to the DateMaker function we wrote
      
      ### Modifying SD estimates based on anomalous readings in the training data
      UCL0=c(rep(xBarLimit1,length(ind01)),rep(xBarLimit2,length(ind02)))*histsd ### Note that we don't want to filter out the changes in the testing data, so xBarLimit2 is much larger!
      x=x0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      y=y0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      ind=ind0[myPixel0>lowthresh & abs(y0)<UCL0] ### Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
      histsd=sd(y01[which(myPixel1>lowthresh & abs(y01)<UCL0[1:historybound01])]) ### Updating the training SD estimate.  This is the all-important driver of the EWMA control limits.
      if(is.na(histsd)==1){return(tmp)
                           break}
      
      Totals=y0*0 ### Future EWMA output
      tmp2=rep(-2222,length(y)) ### Coded values for the 'present' subset of the data
      
      ewma=y[1] ### Initialize the EWMA outputs with the first present residual
      for(i in (2):length(y)){ 
        ewma=c(ewma,(ewma[(i-1)]*(1-lambda)+lambda*y[i])) ### Appending new EWMA values for all present data.
      }
      
      UCL=histsd*lambdasigs*sqrt(lambda/(2-lambda)*(1-(1-lambda)^(2*c(1:length(y))))) ### EWMA upper control limit.  This is the threshold which dictates when the chart signals a disturbance.
      
      if(rounding==TRUE){tmp2=sign(ewma)*floor(abs(ewma/UCL))} ### Integer value for EWMA output relative to control limit (rounded towards 0).  A value of +/-1 represents the weakest disturbance signal
      if(rounding==FALSE){tmp2=round(ewma,0)} ### EWMA outputs in terms of resdiual scales.  
      
      ###  Keeping only values for which a disturbance is sustained, using persistence as the threshold
      if(persistence>1 & length(tmp2)>3){ ### Ensuring sufficent data for tmp2
        tmpsign=sign(tmp2) # Disturbance direction
        shiftpoints=c(1,which(tmpsign[-1]!=tmpsign[-length(tmpsign)]),length(tmpsign)) # Dates for which direction changes
        
        tmp3=rep(0,length(tmpsign))
        for(i in 1:length(tmpsign)){  # Counting the consecutive dates in which directions are sustained
          tmp3lo=0
          tmp3hi=0
          
          while(((i-tmp3lo)>0)){if((tmpsign[i]-tmpsign[i-tmp3lo])==0){tmp3lo=tmp3lo+1} else{break}}
          while(((tmp3hi+i)<=length(tmpsign))){if((tmpsign[i+tmp3hi]-tmpsign[i])==0){tmp3hi=tmp3hi+1} else{break}}
          tmp3[i]=tmp3lo+tmp3hi-1
          
        }
        
        tmp4=rep(0, length(tmp3)) 
        for(i in 1:length(tmp3)){ # If sustained dates are long enough, keep; otherwise set to previous sustained state
          if(tmp3[i]>=persistence){tmp4[i]=tmp2[i]} else {tmp4[i]=max(tmp2[which.max(tmp3[which(tmp3[1:i]>=persistence)])],0)}
        }
        
        tmp2=tmp4
        
      }
      
      tmp[bkgd.ind00[ind]]=tmp2 ### Assigning EWMA outputs for present data to the original template.  This still leaves -2222's everywhere the data was missing or filtered.
      
      if(tmp[1]==-2222){ ### If the first date of myPixel was missing/filtered, then assign the EWMA output as 0 (no disturbance).
        tmp[1]=0
      }
      
      if(tmp[1]!=-2222){ ### If we have EWMA information for the first date, then for each missing/filtered date in the record, fill with the last known EWMA value
        for(stepper in 2:Dates){
          if(tmp[stepper]==-2222){tmp[stepper]=tmp[stepper-1]}
        }
      }
      
    }
  }
  return(as.integer(tmp)) ### Final output.  All -2222's if data were insufficient to run the algorithm, otherwise an EWMA record of relative (rounded=T) or raw-residual (rounded=F) format.
}


## Chunk-based function
EWMACD.in.rasterEngine=function(x,...){
  tmp=apply(x,c(1:2),FUN=EWMACD.pixel.for.rasterEngine,nc=nc,ns=ns,DOYs=DOYs,Years=Years,
            historybound=historybound,xBarLimit1=xBarLimit1,xBarLimit2=xBarLimit2,lowthresh=lowthresh,lambdasigs=lambdasigs,
            lambda=lambda,rounding=rounding,persistence=persistence,trainingStart=trainingStart,trainingEnd=trainingEnd,testingEnd=testingEnd)
  tmp=aperm(tmp,c(2,3,1))
  return(tmp)
  #   return(array(DOYs,dim=c(dim(x)[1],dim(x)[2],length(DOYs))))
}


## Wrapper (incorporates parallel processing capability)
EWMACD.rasterEngine=function(inputBrick,DateInfo,trainingStart,trainingEnd,testingEnd,numberHarmonics=2,xBarLimit1=1.5,xBarLimit2=20,lowthresh=100,
                             lambda=0.3,lambdasigs=3,rounding=T,persistence=3,numberCPUs='all',writeFile=F,fileName=paste('EWMACD_Outputs',sep=''),...){
  if(numberCPUs=='all'){sfQuickInit()} else {sfQuickInit(numberCPUs)}
  
  ns=nc=numberHarmonics
  DOYs=DateInfo$DOY
  Years=DateInfo$Year
  
  trims=which(Years>=trainingStart & Years<testingEnd) # Subsets DateInfo to desired training and testing periods
  DateInfo2=DateInfo[trims,] # Adds it back to the list
  DOYs=DateInfo2$DOY
  Years=DateInfo2$Year
  inputBrick=subset(inputBrick,trims)
  
  historybound=max(which(Years<trainingEnd))
  
  
  executionTime= system.time((
    tmpOutput=rasterEngine(x=inputBrick,
        fun=EWMACD.in.rasterEngine,args=list(EWMACD.pixel.for.rasterEngine=EWMACD.pixel.for.rasterEngine,nc=nc,ns=ns,DOYs=DOYs,Years=Years,
        historybound=historybound,xBarLimit1=xBarLimit1,xBarLimit2=xBarLimit2,lowthresh=lowthresh,lambdasigs=lambdasigs,
        lambda=lambda,rounding=rounding,persistence=persistence,trainingStart=trainingStart,trainingEnd=trainingEnd,testingEnd=testingEnd))
  ))[3]
  sfQuickStop()
  
  if(writeFile==T){write.EWMACD(tmpOutput,fileName,DateInfo=DateInfo2,trainingStart=trainingStart,testingEnd=testingEnd)}
  
  output=list(tmpOutput,executionTime)
  names(output)=c('EWMACD','executionTime')
  return(output)
  
}

## Testing the function
# test4=EWMACD.rasterEngine(inputBrick=dat,DateInfo=DateInfo,trainingStart=2005,trainingEnd=2007,testingEnd=2009,writeFile=T,fileName='New Test 3')
# plot(test4$EWMACD,51,col=EWMAcolorbar,zlim=c(-15,15))

###################################################################
###### Examples using EWMACD (Optional)

#Results=EWMACD.rasterEngine(inputBrick=dat,DateInfo=DateInfo,trainingStart=2005,trainingEnd=2009,testingEnd=2012)$EWMACD

## Plotting
#EWMAcolorbar=c(colorRampPalette(c('red','orange','yellow'))(1000),NA,colorRampPalette(c('green','darkgreen'))(1000))
#NAvalue(Results)=-2222 # Sets the coded missing data value to NA

#Aerial09=brick('Sample Data NAIP Image 2009.envi')
#Aerial11=brick('Sample Data NAIP Image 2011.envi')

#par(mfcol=c(2,2))
#plotRGB(aggregate(Aerial09,by=1),1,2,3)
##plot(Results,nlayers(Results),col=EWMAcolorbar,zlim=c(-10,10)) # Plots the final EWMACD output layer (reds for removal, greens for growth)
