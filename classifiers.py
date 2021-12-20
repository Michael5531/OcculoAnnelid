import serial
import time
import numpy as np
import wave
import rpy2
import sys
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector
import os

robjects.r("""
        ## R studio reading wave
        read_wave <- function(path){

            library(tuneR)
            dir_long <- path
            all_files_long <- list.files(dir_long)

            wave_file_long <- list()
            label_long <- list()

            for (i in all_files_long) {
                    wave_file_long[[i]] <- tuneR::readWave(file.path(dir_long, i))
                    label_long <- c(label_long,  strsplit(i, "_")[[1]][1] )
            }

            predicted_label_and_time <- lapply(wave_file_long, streaming_classifier)
            return(predicted_label_and_time)

        }

        LR_detection <- function(seq) {

            # Index of the max
            maxval <- which.max(na.omit(seq))

            # Index of the min
            minval <- which.min(na.omit(seq))

            # If max occurs before min then left otherwise right
            movement <- ifelse(maxval < minval,  "L", "R")
            return(movement)
        }
        streaming_classifier <- function(wave_file,
                                window_size = wave_file@samp.rate ,
                                increment = window_size/10,
                                thresholdEvents = 30) {
            # Extract the signal from WAV file
            Y = wave_file@left

            # Time (in seconds) of the sequencing
            xtime = seq_len(length(wave_file@left))/wave_file@samp.rate

            # Storing our predictions in these vectors later
            predicted_labels <- c()
            predicted_time <- c()

            # Lower bound for our current interval
            lower_interval = 1

            # Maximum time (our interval cannot exceed this)
            max_time = max(xtime)*window_size

            while(max_time > lower_interval + window_size) {

                # Upper bound for our current interval
                upper_interval = lower_interval + window_size

                # Signal for our current interval
                interval = Y[lower_interval:upper_interval]

                # Compute our test statistic (number of zero-crossings within the interval)
                testStat <- sum(interval[1:(length(interval) - 1)] * interval[2:(length(interval))] <= 0)

                # Use threshold to determine eye movement intervals
                if (testStat < thresholdEvents) {
                # Make a prediction using our LR_detection function
                        predicted = LR_detection(interval)
                        # Store our predictions and times
                        predicted_labels = c(predicted_labels, predicted)
                        predicted_time = c(predicted_time, lower_interval + window_size/2)
                        lower_interval <- lower_interval + window_size
                } else {
                    lower_interval <- lower_interval + increment
                }

            } ## end while

            return(data.frame(predicted_labels, predicted_time))
        }## end function
        ##testing
        test_function <- function(a, b){
            return(a+b)
        }
""")

# wave_file = wave.open('Training Data/periodic_right/periodic_right_damian.wav')
# wave_file.close()
# samp_rate = wave_file.getframerate()

##just for testing

# Option2
# Rcode = """
# library(tuneR)
# dir_long <- "Training Data/test"
# all_files_long <- list.files(dir_long)

# wave_file_long <- list()
# label_long <- list()
# for (i in all_files_long) {
#   wave_file_long[[i]] <- tuneR::readWave(file.path(dir_long, i))
#   label_long <- c(label_long,  strsplit(i, "_")[[1]][1] )
# }
# predicted_label_and_time <- lapply(wave_file_long, streaming_classifier)
# predicted_label_and_time

# """
# t = r(Rcode)
# print(t)
utils = rpackages.importr('utils')

# select a mirror for R packages
utils.chooseCRANmirror(ind=1) # select the first mirror in the list


packnames = ('ggplot2', 'tuneR','tesfeatures')

# R vector of strings
from rpy2.robjects.vectors import StrVector

# Selectively install what needs to be install.
# We are fancy, just because we can.
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))

tuneR = importr('tuneR')
# tsfeatures = importr('tesfeatures')
path = "Training Data/test"
result = robjects.r['read_wave'](path)
print(result)



# robjects.r("""

#     library(tsfeatures)
#     Y_list = unlist(wave_seq_short, recursive=FALSE)
#     Y_lab = unlist(wave_label_short)

#     Y_features <- cbind(
#     tsfeatures(Y_list,
#              c("acf_features","entropy","lumpiness",
#                "flat_spots","crossing_points")),
#   tsfeatures(Y_list, "max_kl_shift", width=48),
#   tsfeatures(Y_list,
#              c("mean","var"), scale=FALSE, na.rm=TRUE),
#   tsfeatures(Y_list,
#              c("max_level_shift","max_var_shift"), trim=TRUE)) 
#     X = as.matrix(Y_features)
#     y = Y_lab 

#     cvK = 5  # number of CV folds
#     cv_50acc5_knn = cv_acc5 = c()
#     for (i in 1:50) {
#         cvSets = cvTools::cvFolds(nrow(X), cvK)  # permute all the data, into 5 folds
  
#         cv_acc = NA  # initialise results vector
#     for (j in 1:cvK) {
#         test_id = cvSets$subsets[cvSets$which == j]
#         X_test = X[test_id, ]
#         X_train = X[-test_id, ]
#         y_test = y[test_id]
#         y_train = y[-test_id]
#         fit = class::knn(train = X_train, test = X_test, cl = y_train, k = 3)
#         cv_acc5[j] = table(fit, y_test) %>% diag %>% sum %>% `/`(length(y_test))
#   }
#   cv_50acc5_knn <- append(cv_50acc5_knn, mean(cv_acc5))
# }

# boxplot(cv_50acc5_knn, horizontal = TRUE, xlab="Accuracy")
# """)





# streaming_classifier: robjects.r['streaming_classifier'](wave_file,
#                                 window_size = samp_rate ,
#                                 increment = samp_rate/10,
#                                 thresholdEvents = 30)

sys.exit()

# test = streaming_classifier(wave_file,samp_rate, samp_rate/10, 30)


