# A simple regression example with the Gaussian Mixture Model (GMM)

import pypr.clustering.gmm as gmm

np.random.seed(1)

N = 100
remove_factor = 0.1 # Removes two times this from the middle (0.5 = remove all)
x = np.linspace(0, 2*np.pi, N)
x = np.concatenate((x[:N*(0.5-remove_factor)], x[N*(0.5+remove_factor):]))
y = np.sin(x) + 0.1 * np.random.normal(size=len(x))

K = 6 # Number of clusters to use
X = np.concatenate((np.c_[x],np.c_[y]), axis=1)
cluster_init_kw = {'cluster_init':'kmeans', 'max_init_iter':5, \
    'cov_init':'var', 'verbose':True}
cen_lst, cov_lst, p_k, logL = gmm.em_gm(X, K = K, max_iter = 2000, \
    delta_stop=1e-5, init_kw=cluster_init_kw, verbose=True, max_tries=100)

plot(X[:,0], X[:,1], 'o', label='Input data')

M = 1000 # Points in prediction
xx = np.linspace(-2, 2*np.pi+2, M)
XX = np.concatenate((np.c_[xx],np.c_[xx]*np.nan), axis=1)
sigma_lst = []
for i in range(XX.shape[0]):
    y, sigma = gmm.cond_moments(XX[i,:], cen_lst, cov_lst, p_k)
    XX[i, 1] = y
    sigma_lst.append(sigma[0][0])
#var = gmm.predict(XX, cen_lst, cov_lst, p_k) # Predict them again
#std = [np.sqrt(v[0][0]) for v in var]
std = [np.sqrt(v) for v in sigma_lst]
plot(XX[:,0], XX[:,1], label='Predicted output', lw = 2)
plot(XX[:,0], XX[:,1] - std, 'k--', label='Std. dev.')
plot(XX[:,0], XX[:,1] + std, 'k--')
legend()

# Plot the cluster ellipses
for i in range(len(cen_lst)):
    x1,x2 = gmm.gauss_ellipse_2d(cen_lst[i], cov_lst[i])
    plot(x1, x2, 'k', linewidth=2)

O = 0
xxx = np.linspace(-2, 2*np.pi+2, O)
for x in xxx:
    inp = np.array([x, np.nan])
    cen_cond, cov_cond, mc_cond = gmm.cond_dist(inp, cen_lst, cov_lst, p_k)
    y = np.linspace(-1.5, 1.5, 100)
    x2plt = gmm.gmm_pdf(c_[y], cen_cond, cov_cond, mc_cond)
    plot(x+x2plt*0.1, y, 'k')


