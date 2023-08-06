# Compute features for 1 in every 10 frames of the input. This avoids us to
# analyze the whole video. If you want to be thorough, put `1` here, but be
# warned this will generate a lot of data.
every_n_frames = 10

# Cropping
CROP_EYES_D = 33
CROP_H = 80
CROP_W = 64
CROP_OH = 16
CROP_OW = 32

# Tan Triggs
GAMMA = 0.2
SIGMA0 = 1.
SIGMA1 = 2.
SIZE = 5
THRESHOLD = 10.
ALPHA = 0.1

# DCT blocks
BLOCK_H = 8
BLOCK_W = 8
OVERLAP_H = 7
OVERLAP_W = 7
N_DCT_COEF = 28

# 3. UBM
frames_to_use = 375 #use up to frame #375
nb_gaussians = 512 #number of gaussians on the mixture model
iterk = 500 #number of kmeans (em) iterations (default to 500)
iterg_train = 500 #number of gmm (em) iterations (default to 500)
end_acc = 0.0005
var_thd = 0.0005
update_weights = True
update_means = True
update_variances = True
norm_KMeans = True

# 4. GMM
iterg_enrol = 1 #number of adaptation iterations
convergence_threshold = 0.0005
variance_threshold = 0.0005
relevance_factor = 4
responsibilities_threshold = 0
linear_scoring = True
zt_norm = False
