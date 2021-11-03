import numpy as np
from pmagpy import pmag
from sklearn.decomposition import PCA
import scipy.linalg as la


def fisher_stat(data, selected_dots, system):
    col_D = "Dg"
    col_I = "Ig"
    if system == "stratigraphic":
        col_D = "Ds"
        col_I = "Is"

    do_fisher_list = []
    for i in selected_dots:
        do_fisher_list.append([data[col_D][i], data[col_I][i], 1.0])

    fisher_mean_stat = pmag.fisher_mean(do_fisher_list)
    a95, K, D, I = fisher_mean_stat["alpha95"], fisher_mean_stat["k"], fisher_mean_stat["dec"], fisher_mean_stat["inc"]
    xm, ym, zm = dir_to_xyz(D, I, 1)

    Rs = np.sqrt(xm ** 2 + ym ** 2 + zm ** 2)
    xm /= Rs
    ym /= Rs
    zm /= Rs
    return a95, K, Rs, D, I, xm, ym, zm


    # xs = 0
    # ys = 0
    # zs = 0
    # a95 = 0  # the radius of the confidence circle
    # Rs = 1  # average vector always has the length of 1 because all vectors have the same length of 1
    # n = len(selected_dots)
    # for i in selected_dots:
    #     rI = np.radians(float(data[col_I][i]))
    #     rD = np.radians(float(data[col_D][i]))
    #     xs += np.cos(rI) * np.cos(rD)
    #     ys += np.cos(rI) * np.sin(rD)
    #     zs += np.sin(rI)  # because all vectors have a length of 1
    # # xyzDIR
    # Rs = np.sqrt(xs**2 + ys**2 + zs **2)
    # Dm = np.degrees(np.arccos(xs / np.sqrt(xs**2 + ys**2)))
    # if ys < 0: Dm = -Dm
    # dr = Dm - 360 * int(Dm / 360)
    # if dr < 0: dr += 360
    # Dm = dr
    # Im = np.degrees(np.arcsin(zs / Rs))
    # # normalized x, y, z
    # xm = xs/Rs
    # ym = ys/Rs
    # zm = zs/Rs
    # # because of all vectors is have the length of 1, ipar <= 1 is True and then:
    # Rm = Rs / n  # normalized length of the average vector
    # k = (n - 1) / (n - Rs)
    # if k < 4:
    #     if Rm <= 0.001:
    #         k = 3 * Rm
    #         a95 = 180
    #         return a95, k, Rs, Dm, Im, xm, ym, zm
    #     k = 20
    #     while True:
    #         cth = (1 + np.exp(-2 * k) / (1 - np.exp(-2 * k)))
    #         k1 = 1 / (cth - Rm)
    #         if abs(k - k1) <= 0.01:
    #             k = k1
    #             break
    #         k = k1
    #     a95 = np.degrees(np.arccos(1 + np.log(1 - 0.95 * (1 - np.exp(-2 * k))) / k))
    #     return a95, k, Rs, Dm, Im, xm, ym, zm
    # a95 = np.degrees(np.arccos(1 - 2.9957 / (n * k)))
    # return a95, k, Rs, Dm, Im, xm, ym, zm


def bingham_stat(data, selected_dots, system, mode):
    # Look at Onstott, 1980 (doi:10.1029/jb085ib03p01500)

    col_D = "Dg"
    col_I = "Ig"
    if system == "stratigraphic":
        col_D = "Ds"
        col_I = "Is"

    dobingham_list = []
    for i in selected_dots:
        dobingham_list.append([data[col_D][i], data[col_I][i]])

    if mode == "zero_mode":
        I_zero, D_zero = xyz_to_dir(0,0,0,"single")
        dobingham_list.append([D_zero, I_zero])
    bing_mean_stat = pmag.dobingham(dobingham_list)
    # "_min" - for minor axis of trust ellipse
    # "_max" - for major axis of trust ellipse

    I_min, D_min, a95_min = bing_mean_stat["Zinc"], bing_mean_stat["Zdec"], bing_mean_stat["Zeta"]
    I_max, D_max, a95_max = bing_mean_stat["Einc"], bing_mean_stat["Edec"], bing_mean_stat["Eta"]

    return I_min, D_min, a95_min, I_max, D_max, a95_max


# PCA
def newton(root, eps, a, b, c, kmax):
    x = root
    for i in range(1, kmax+1, 1):
        y = x-(a+x*(b+x*(c+x)))/(b+x*(2*c+3*x))
        if abs(x-y) <= eps:
            return y, i
        x = y
    return x, 21


def root3(a):
    kmax = 20
    a0 = a[0]
    a1 = a[1]
    a2 = a[2]
    x = 1
    x, ierr = newton(x, 10**(-5), a0, a1, a2, kmax)
    root_1 = x  # first root

    # p = a[2] + x
    # q = a[1] + x*p
    # d = np.sqrt(p**2 - 4*q)
    # x = (d - p)/2
    # x, ierr = newton(x, 10**(-5), p0, p1, p2, kmax)
    # root_2 = x  # second root
    #
    # x = -(p + d)/2
    # x, ierr = newton(x, 10**(-5), p0, p1, p2, kmax)
    # root_3 = x  # third root
    #
    # roots = [root_1, root_2, root_3]
    # roots = sorted(roots)
    # x = roots[0]
    # x, ierr = newton(x, 10**(-8), p0, p1, p2, kmax)
    # roots[0] = x

    b0 = -a0/root_1
    b1 = a2 + x
    b2 = 1
    other_roots = np.roots([b2, b1, b0])
    root_2 = other_roots[0] # second root
    root_3 = other_roots[1] # third root
    roots = [root_1, root_2, root_3]
    roots = sorted(roots)

    x = roots[0]
    x, ierr = newton(x, 10**(-8), a0, a1, a2, kmax)
    roots[0] = x

    return roots


def halls(data, selected_dots, system, approx_mode):
    col_D = "Dg"
    col_I = "Ig"
    if system == "stratigraphic":
        col_D = "Ds"
        col_I = "Is"

    n = len(selected_dots)
    if approx_mode == 'zero-mode':
        n += 1
    dm = []
    im = []
    a95 = []
    a1 = b1 = c1 = d1 = e1 = f1 = 0
    r1_0 = 1
    for i in selected_dots:
        x, y, z = dir_to_xyz(data[col_D][i], data[col_I][i], r1_0)
        a1 += x**2
        b1 += y**2
        c1 += z**2
        d1 += x*y
        e1 += x*z
        f1 += y*z
    d2 = d1**2
    e2 = e1**2
    f2 = f1**2
    a = []
    a.append(a1*f2 + b1*e2 + c1*d2 - a1*b1*c1 - 2*d1*e1*f1)
    a.append(a1*b1 + b1*c1 + a1*c1 - d2 - e2 - f2)
    a.append(-(a1 + b1 + c1))
    a.append(1)
    roots = root3(a)
    for i in range(0, 3, 1):
        ap = a1 - roots[i]
        bp = b1 - roots[i]
        de = d1*f1 - bp*e1
        y = (d1*e1 - ap*f1)/de
        z = (ap*bp - d2)/de
        im_i, dm_i = xyz_to_dir(1, y, z, 'single')
        dm.append(dm_i)
        im.append(im_i)

    tt = roots[0]*np.exp(2/(n-2)*np.log(20)-1)
    z1 = tt/(roots[1]-roots[0])
    z2 = tt/(roots[2]-roots[0])
    if z1 <= 0:
        z1 = 0
        a95.append(0)
    elif z1 > 0.9999:
        a95.append(999)
    else:
        a95.append(np.degrees(np.arcsin(np.sqrt(z1))))

    if z2 <= 0:
        z2 = 0
        a95.append(0)
    elif z2 > 0.9999:
        a95.append(999)
    else:
        a95.append(np.degrees(np.arcsin(np.sqrt(z2))))

    # # cheat!!!
    # w, v = np.linalg.eig(np.matrix([
    #     [a1, d1, e1],
    #     [d1, b1, f1],
    #     [e1, f1, c1]
    # ]))
    # v = v.tolist()
    # v = sorted(v)
    # d_cheat = []
    # i_cheat = []
    # for i in range(0, 3, 1):
    #     x = v[i][0]
    #     y = v[i][1]
    #     z = v[i][2]
    #     I, D = xyz_to_dir(x, y, z, 'single')
    #     d_cheat.append(D)
    #     i_cheat.append(I)
    # # end cheat


def pca(data, selected_dots, system, approx_mode):
    print(data, selected_dots, system, approx_mode)
    df = data
    n = len(selected_dots)
    col_D = "Dg"
    col_I = "Ig"

    if system == "stratigraphic":
        col_D = "Ds"
        col_I = "Is"

    first_col_name = "T"
    if "M" in df.columns:
        first_col_name = "M"

    df["quality"] = "g"
    data_to_pca = df[[first_col_name, col_D, col_I, "MAG", "quality"]].values.tolist()
    answer = pmag.domean(data_to_pca, 0, n-1, approx_mode)
    return answer["specimen_inc"], answer["specimen_dec"], answer["specimen_mad"]


    # if approx_mode != "zero-mode":
    #     for i in selected_dots:
    #         x, y, z = dir_to_xyz(data[col_D][i], data[col_I][i], 1)
    #         xm += x
    #         ym += y
    #         zm += z
    #     xm /= n
    #     ym /= n
    #     zm /= n
    #
    # for i in selected_dots:
    #     x, y, z = dir_to_xyz(data[col_D][i], data[col_I][i], 1)
    #     xx += (x-xm)**2
    #     yy += (y-ym)**2
    #     zz += (z-zm)**2
    #     xy += (x-xm)*(y-ym)
    #     yz += (y-ym)*(z-zm)
    #     zx += (z-zm)*(x-xm)
    #
    # norm = xx
    # pca_matrix = np.array([
    #     [xx, xy, zx],
    #     [xy, yy, yz],
    #     [zx, yz, zz],
    # ])
    # if approx_mode == "zero-mode":
    #     pca_matrix = pca_matrix/norm
    #
    # eigvals, eigvecs = jacobi_iteration(pca_matrix, )
    # eigvals = np.sort(eigvals)
    # MAD = np.degrees(np.arctan(np.sqrt((eigvals[1] + eigvals[0]) / eigvals[2])))
    # lowx, lowy, lowz = dir_to_xyz(data[col_D][0], data[col_I][0], 1)
    # mmx = lowx - xm
    # mmy = lowy - ym
    # mmz = lowz - zm
    # module = np.sqrt(mmx**2 + mmy**2 + mmz**2)
    # vecs = np.array([eigvecs[0][0], eigvecs[0][1], eigvecs[0][2]])
    # vecs *= module
    # for i in range(3):
    #     vecs = np.array([eigvecs[i][0], eigvecs[i][1], eigvecs[i][2]])
    #     # vecs *= module
    #     I, D = xyz_to_dir(vecs[0], vecs[1], vecs[2], "solo")
    #     print(I, D)
    # print(MAD)


def jacobi_iteration(matrix, rhs_vector):
    ITERATION_LIMIT = 1000

    answer = np.zeros_like(rhs_vector)
    for it_count in range(ITERATION_LIMIT):
        print("Current solution:", answer)
        answer_new = np.zeros_like(answer)

        for i in range(matrix.shape[0]):
            s1 = np.dot(matrix[i, :i], answer[:i])
            s2 = np.dot(matrix[i, i + 1:], answer[i + 1:])
            answer_new[i] = (rhs_vector[i] - s1 - s2) / matrix[i, i]

        if np.allclose(answer, answer_new, atol=1e-10, rtol=0.):
            break

        answer = answer_new

    return answer


def give_principal_components(data, full_data, selected_dots, pca_mode):
    if pca_mode == "DE-BFL-O":
        np.append(data, [0,0])
    # data centering
    m = np.array([data[:,0].mean(), data[:,1].mean()])
    data_centered = data - m
    # sklearn pca
    model = PCA(n_components=2)
    if pca_mode == "DE-BFL-O":
        model.fit(data)
    else:
        model.fit(data_centered)
    w_pca = model.components_
    pca_x = data_centered[:, 0] + m[0]
    pca_y = -(w_pca[1, 0] / w_pca[1, 1]) * data_centered[:, 0] + m[1]
    if pca_mode == "DE-BFL-O":
        pca_x = data[:,0]
        pca_y = -(w_pca[1, 0] / w_pca[1, 1])*data[:,0]

    # if pca_mode == "DE-BFL-O":
    #     pca_x = data_centered[:, 0]
    #     pca_y = -(w_pca[1, 0] / w_pca[1, 1]) * data_centered[:, 0]

    return (
        pca_x,
        pca_y
    )


# sup-func
def kb_for_xy(x1, x2, y1, y2):
    k = (y1-y2)/(x1-x2)
    b = y1 - x1*k
    return k, b


def give_y_from_x(k, b, xs):
    y = []
    for x in xs:
        y.append(k*x+b)
    return y


def xy_solution(k1, b1, k2, b2):
    x = (b2-b1)/(k1-k2)
    y = k1*x + b1
    return x, y


def xyz_to_dir(x, y, z, type):
    if type == "multi":
        D = np.degrees(np.arctan(y/x))
        I = np.degrees(np.arcsin(z))
        for i in range(len(D)):
            if y[i] < 0:
                D[i] = -D[i]
            dr = D[i] - 360*int(D/360)
            if dr < 0:
                dr += 360
            D[i] = dr
        return I, D
    Rs = np.sqrt(x * x + y * y + z * z)
    D = np.degrees(np.arccos(x / np.sqrt(x * x + y * y)))
    if Rs == 0: D = np.degrees(np.arccos(0))
    if y < 0:
        D = -D
    dr = D - 360 * int(D / 360)
    if dr < 0:
        dr += 360
    D = dr
    I = np.degrees(np.arcsin(z / Rs))
    if Rs == 0: I = np.degrees(np.arcsin(0))
    if type == "MAG":
        return round(D, 1), round(I, 1), round(Rs, 1)
    return I, D


def dir_to_xyz(d, i, r):
    d = np.radians(d)
    i = np.radians(i)
    x = r * np.cos(i) * np.cos(d)
    y = r * np.cos(i) * np.sin(d)
    z = r * np.sin(i)
    return x, y, z


def cart_to_dir(x, y, z):
    D = np.degrees(np.arctan(y/x))
    I = np.degrees(np.arcsin(z))
    for i in range(len(D)):
        if y[i] < 0:
            D[i] = -D[i]
        dr = D[i] - 360*int(D/360)
        if dr < 0:
            dr += 360
        D[i] = dr
    r = np.sqrt(x * x + y * y + z * z)
    return I, D, r


def intensity_to_specimen(X, Y, Z):
    X_spec = []
    Y_spec = []
    Z_spec = []

    for k in range(len(X)):
        x = X[k]
        y = Y[k]
        z = Z[k]

        intensity = np.sqrt(x**2 + y**2 + z**2)

        if x < 0:
            if np.degrees(np.arctan(y/x)) < 0:
                d = np.arctan(y/x) + 360
            else:
                d = np.arctan(y/x)
        else:
            if np.degrees(np.arctan(y/x)) + 180 < 0:
                d = np.arctan(y/x) + 180 + 360
            else:
                d = np.arctan(y/x) + 180

        i = np.arcsin(z/intensity)

        X_spec.append(np.cos(i) * np.cos(d))
        Y_spec.append(np.cos(i) * np.sin(d))
        Z_spec.append(np.sin(i))

    X_spec = np.array(X_spec)
    Y_spec = np.array(Y_spec)
    Z_spec = np.array(Z_spec)

    return X_spec, Y_spec, Z_spec


def xyz_to_xyz_geol(x, y, z, a, b):
    sin_a = np.sin(np.radians(a))
    sin_b = np.sin(np.radians(b))
    cos_a = np.cos(np.radians(a))
    cos_b = np.cos(np.radians(b))
    x_geol = x*cos_a*cos_b - y*sin_a - z*cos_a*sin_b
    y_geol = x*sin_a*cos_b + y*cos_a - z*sin_a*sin_b
    z_geol = x*sin_b + z*cos_b
    return x_geol, y_geol, z_geol


def xyz_geol_to_xyz_strat(x, y, z, s, d):
    sin_s = np.sin(np.radians(s))
    sin_d = np.sin(np.radians(d))
    cos_s = np.cos(np.radians(s))
    cos_d = np.cos(np.radians(d))
    tmp_x = x*cos_s*cos_d + y*sin_s*cos_d + z*sin_d
    tmp_y = -x*sin_s + y*cos_s
    x_strat = tmp_x*cos_s - tmp_y*sin_s
    y_strat = tmp_x*sin_s - tmp_y*cos_s
    z_strat = -x*cos_s*sin_d - y*sin_s*sin_d + z*cos_d
    return x_strat, y_strat, z_strat

def paleo_pole(lat, long, d, i, a95):
    d = np.radians(d)
    i = np.radians(i)
    lat = np.radians(lat)
    long = np.radians(long)
    geo_lat = np.arctan(0.5*np.tan(i))
    pole_lat = np.arcsin(np.sin(lat)*np.sin(geo_lat)+np.cos(lat)*np.cos(geo_lat)*np.cos(d))
    pole_long = np.arcsin(np.cos(geo_lat)*np.sin(d)/np.cos(pole_lat))
    if np.sin(geo_lat) >= np.sin(lat)*np.sin(pole_lat):
        pole_long += long
    else:
        pole_long -= (np.radians(180) + long)
        pole_long *= -1
    dm = a95*np.sin(np.arctan(2/np.tan(np.mean(i))))/np.cos(np.mean(i))
    dp = 2*a95/(1+3*np.cos(np.mean(i))**2)
    PaleoLat = np.arctan(0.5*np.tan(np.mean(i)))
    return [
        round(np.degrees(pole_lat), 2),
        round(np.degrees(pole_long), 2),
        round(dp, 2),
        round(dm, 2),
        round(np.degrees(PaleoLat), 2),
    ]