import numpy as np
import cmath
import matplotlib.pyplot as plt
from tqdm import tqdm


def calculate_spectrum(ntp_val, cep1_val):
    # 定义常量
    global ntp, cep1
    ntp = ntp_val
    cep1 = cep1_val

    # 减小 nnk 和 nnt 的值
    nnk = 12
    nnt = 12
    nvar = 4
    npp = nnt * (1 + nnk) * nnk // 2
    # 减小 ntm 的值
    ntm = 512
    ntmax = ntm * ntp
    fm1 = 0.002
    omg1 = 45.56 / 800
    ppi = np.pi
    period = 2 * ppi / omg1
    dtk = period / ntm
    ur = complex(1, 0)
    ui = complex(0, 1)
    epp = 0
    vff = 137 / 300
    tss = 0.5 * (45.56 / 800)
    kkb = 1.3806503 * 1e-23 * 273
    kkb1 = kkb / (1.60218 * 1e-19) / 27.2
    uup = 0

    # 定义函数
    def axs():
        t0 = 0
        tcenter = (ntmax / 2) * dtk
        return t0, tcenter

    def alaserx(tt):
        t0, tcenter = axs()
        return (1 / (1 + epp ** 2) ** 0.5) * fm1 * np.cos(omg1 * (tt - tcenter) + cep1) * (
                np.cos(ppi * (tt - tcenter) / ntp / period) ** 4)

    def alasery(tt):
        t0, tcenter = axs()
        return (epp / (1 + epp ** 2) ** 0.5) * fm1 * np.sin(omg1 * (tt - tcenter)) * (
                np.cos(ppi * (tt - tcenter) / ntp / period) ** 4)

    def evv(kxx, kyy):
        return -vff * (kxx ** 2 + kyy ** 2) ** 0.5

    def ecc(kxx, kyy):
        return vff * (kxx ** 2 + kyy ** 2) ** 0.5

    def themm(kxx, kyy):
        return np.arctan2(kyy, kxx)

    def ddx(kxx, kyy):
        return 0.5 * kyy / (kxx ** 2 + kyy ** 2)

    def ddy(kxx, kyy):
        return -0.5 * kxx / (kxx ** 2 + kyy ** 2)

    def deevx(kxx, kyy):
        return -vff * kxx / (kxx ** 2 + kyy ** 2) ** 0.5

    def deevy(kxx, kyy):
        return -vff * kyy / (kxx ** 2 + kyy ** 2) ** 0.5

    def deecx(kxx, kyy):
        return -vff * kxx / (kxx ** 2 + kyy ** 2) ** 0.5

    def deecy(kxx, kyy):
        return -vff * kyy / (kxx ** 2 + kyy ** 2) ** 0.5

    # 主程序
    pmax = 0.25
    dpp = 0.25 / nnk
    pps = np.zeros(nnk)
    dth = np.zeros(nnk)
    thek = np.zeros((nnk, nnt * nnk))
    pxt = np.zeros((nnk, nnt * nnk))
    pyt = np.zeros((nnk, nnt * nnk))
    pxt1 = np.zeros((nnk, nnt * nnk))
    pyt1 = np.zeros((nnk, nnt * nnk))
    pssx = np.zeros(npp)
    pssy = np.zeros(npp)
    tp = np.zeros(ntmax)
    elx = np.zeros(ntmax)
    ely = np.zeros(ntmax)
    flx = np.zeros(ntmax)
    fly = np.zeros(ntmax)
    evt = np.zeros(ntmax)
    ect = np.zeros(ntmax)
    thet = np.zeros(ntmax)
    sss1 = np.eye(nvar, dtype=complex)
    hhs1 = np.zeros((nvar, nvar), dtype=complex)
    hhs2 = np.zeros((nvar, nvar), dtype=complex)
    hhs3 = np.zeros((nvar, nvar), dtype=complex)
    hhs4 = np.zeros((nvar, nvar), dtype=complex)
    alp2 = complex(1, 0)
    blp2 = complex(0, 0)
    alp1 = complex(1, 0)
    blp1 = complex(0, 0)
    mats = np.zeros((nvar, nvar), dtype=complex)
    mats1 = np.zeros((nvar, nvar), dtype=complex)
    bd1 = np.zeros((nvar, 1), dtype=complex)
    xd1 = np.zeros((nvar, 1), dtype=complex)
    yps1 = np.zeros(nvar, dtype=complex)
    r1 = np.zeros(nvar)
    c1 = np.zeros(nvar)
    ferr1 = np.zeros(1)
    berr1 = np.zeros(1)
    work1 = np.zeros(2 * nvar, dtype=complex)
    af1 = np.zeros((nvar, nvar), dtype=complex)
    rwork1 = np.zeros(2 * nvar)
    rcond1 = 0
    ipiv1 = np.zeros(nvar, dtype=int)
    info1 = 0
    equed1 = ''
    vm1 = np.zeros(nvar, dtype=complex)
    vv1 = np.zeros(nvar, dtype=complex)
    cccv = 0
    cccc = 0
    sump = 0
    cpcv = complex(0, 0)
    cpcv1 = complex(0, 0)
    devtx = np.zeros(ntmax)
    devty = np.zeros(ntmax)
    dectx = np.zeros(ntmax)
    decty = np.zeros(ntmax)
    ddtx = np.zeros(ntmax)
    ddty = np.zeros(ntmax)
    jjtx = np.zeros(ntmax, dtype=complex)
    jjty = np.zeros(ntmax, dtype=complex)
    jjrx = np.zeros(ntmax, dtype=complex)
    jjry = np.zeros(ntmax, dtype=complex)
    jjtsx = np.zeros(ntmax, dtype=complex)
    jjtsy = np.zeros(ntmax, dtype=complex)
    thm = 0
    ak11 = np.zeros(ntmax, dtype=complex)
    ak22 = np.zeros(ntmax, dtype=complex)
    ak12 = np.zeros(ntmax, dtype=complex)
    ak21 = np.zeros(ntmax, dtype=complex)
    sumttx = np.zeros(ntmax, dtype=complex)
    sumtty = np.zeros(ntmax, dtype=complex)
    # 修改为复数数组
    jjxs = np.zeros(ntmax, dtype=complex)
    jjys = np.zeros(ntmax, dtype=complex)
    jjxs1 = np.zeros(ntmax, dtype=complex)
    jjys1 = np.zeros(ntmax, dtype=complex)
    ww = np.zeros(5 * 50)
    dww = 0.056 / 10 / 375
    accex = np.zeros(ntmax, dtype=complex)
    accey = np.zeros(ntmax, dtype=complex)
    sumex = complex(0, 0)
    sumey = complex(0, 0)
    sumet = complex(0, 0)
    # 修改为复数数组
    ssx = np.zeros(5 * 50, dtype=complex)
    ssy = np.zeros(5 * 50, dtype=complex)
    sst = np.zeros(5 * 50, dtype=complex)
    fpp = np.zeros(npp)
    sumps = 0
    fpp1 = np.zeros(npp)

    # 初始化pps
    for i in range(nnk):
        pps[i] = (i + 1) * dpp

    # 计算thek, pxt, pyt
    for i in range(nnk):
        dth[i] = 2 * ppi / nnt / (i + 1)
        for j in range((i + 1) * nnt):
            thek[i, j] = j * dth[i]
            pxt[i, j] = pps[i] * np.cos(thek[i, j])
            pyt[i, j] = pps[i] * np.sin(thek[i, j])

    # 计算pxt1, pyt1
    for i in range(nnk):
        for j in range((i + 1) * nnt - 1):
            pxt1[i, j] = (pxt[i, j] + pxt[i, j + 1]) / 2
            pyt1[i, j] = (pyt[i, j] + pyt[i, j + 1]) / 2
        ik1 = (i + 1) * nnt - 1
        ik2 = 0
        pxt1[i, ik1] = (pxt[i, ik2] + pxt[i, ik1]) / 2
        pyt1[i, ik1] = (pyt[i, ik2] + pyt[i, ik1]) / 2

    # 计算pssx, pssy
    ip = 0
    for i in range(nnk):
        for j in range((i + 1) * nnt):
            pssx[ip] = pxt1[i, j]
            pssy[ip] = pyt1[i, j]
            ip += 1

    # 计算fpp和sumps
    for i in range(npp):
        fpp[i] = 1 / (1 + np.exp((evv(pssx[i], pssy[i]) - uup) / kkb1))
    sumps = np.sum(fpp)

    # 计算fpp1
    for i in range(npp):
        fpp1[i] = fpp[i] / sumps

    # 计算tp, elx, ely
    t0, tcenter = axs()
    for i in range(ntmax):
        tp[i] = t0 + i * dtk
        elx[i] = alaserx(tp[i])
        ely[i] = alasery(tp[i])

    # 计算flx, fly
    sumtx = 0
    sumty = 0
    for i in range(ntmax):
        sumtx += elx[i] * dtk
        sumty += ely[i] * dtk
        flx[i] = -sumtx
        fly[i] = -sumty

    # 初始化vm1
    vm1[2] = complex(1, 0)

    # 主循环
    for ikk in tqdm(range(npp), desc=f"ntp={ntp_val}, cep1={cep1_val}"):
        thm = themm(pssx[ikk], pssy[ikk])
        for j in range(ntmax):
            ak11[j] = evv(pssx[ikk], pssy[ikk]) - vff * flx[j] * np.cos(thm) - vff * fly[j] * np.sin(thm)
            ak22[j] = ecc(pssx[ikk], pssy[ikk]) + vff * flx[j] * np.cos(thm) + vff * fly[j] * np.sin(thm)
            ak12[j] = ui * vff * fly[j] * np.cos(thm) - ui * vff * flx[j] * np.sin(thm)
            ak21[j] = ui * vff * flx[j] * np.sin(thm) - ui * vff * fly[j] * np.cos(thm)

        for it in range(ntmax):
            vv1 = vm1.copy()
            cccc = vv1[2].real
            cccv = vv1[3].real
            cpcv = vv1[0]
            cpcv1 = vv1[1]

            jjtsx[it] = (cccc - cccv) * np.cos(thm) - ui * np.sin(thm) * (cpcv - cpcv1)
            jjtsy[it] = (cccc - cccv) * np.sin(thm) + ui * np.cos(thm) * (cpcv - cpcv1)

            hhs1[0, 0] = (ak22[it] - ak11[it]) * dtk / 2 - ui * tss * dtk / 2
            hhs1[0, 1] = complex(0, 0)
            hhs1[0, 2] = -ak21[it] * dtk / 2
            hhs1[0, 3] = ak21[it] * dtk / 2
            hhs1[1, 0] = complex(0, 0)
            hhs1[1, 1] = -(ak22[it] - ak11[it]) * dtk / 2 - ui * tss * dtk / 2
            hhs1[1, 2] = ak12[it] * dtk / 2
            hhs1[1, 3] = -ak12[it] * dtk / 2
            hhs1[2, 0] = -ak12[it] * dtk / 2
            hhs1[2, 1] = ak21[it] * dtk / 2
            hhs1[2, 2] = complex(0, 0)
            hhs1[2, 3] = complex(0, 0)
            hhs1[3, 0] = ak12[it] * dtk / 2
            hhs1[3, 1] = -ak21[it] * dtk / 2
            hhs1[3, 2] = complex(0, 0)
            hhs1[3, 3] = complex(0, 0)

            hhs2 = np.dot(hhs1, hhs1)
            hhs3 = np.dot(hhs2, hhs1)
            hhs4 = np.dot(hhs3, hhs1)

            mats = sss1 - ui * hhs1 - hhs2 / 2 + ui * hhs3 / 6 + hhs4 / 24
            mats1 = sss1 + ui * hhs1 - hhs2 / 2 - ui * hhs3 / 6 + hhs4 / 24

            yps1 = np.dot(mats, vm1)
            bd1[:, 0] = yps1

            try:
                xd1[:, 0] = np.linalg.solve(mats1, bd1[:, 0])
            except np.linalg.LinAlgError:
                print("error1")
            vm1 = xd1[:, 0]

        for ixp in range(ntmax):
            sumttx[ixp] += jjtsx[ixp] * fpp1[ikk]
            sumtty[ixp] += jjtsy[ixp] * fpp1[ikk]

    # 计算jjxs, jjys
    for it in range(ntmax):
        jjxs[it] = sumttx[it]
        jjys[it] = sumtty[it]

    # 计算jjxs1, jjys1
    for it in range(ntmax - 1):
        jjxs1[it] = (sumttx[it + 1] - sumttx[it]) / dtk
        jjys1[it] = (sumtty[it + 1] - sumtty[it]) / dtk
    jjxs1[ntmax - 1] = 2 * jjxs1[ntmax - 2] - jjxs1[ntmax - 3]
    jjys1[ntmax - 1] = 2 * jjys1[ntmax - 2] - jjys1[ntmax - 3]

    # 计算ww
    for i in range(5 * 50):
        ww[i] = dww * i

    # 计算accex, accey, sumex, sumey, sumet, ssx, ssy, sst
    for i in tqdm(range(5 * 50), desc=f"Calculating spectrum for ntp={ntp_val}, cep1={cep1_val}"):
        for j in range(ntmax):
            accex[j] = jjxs1[j] * cmath.exp(-ui * ww[i] * tp[j])
            accey[j] = jjys1[j] * cmath.exp(-ui * ww[i] * tp[j])
        sumex = np.trapz(accex, dx=dtk)
        sumey = np.trapz(accey, dx=dtk)
        sumet = sumex + sumey
        ssx[i] = sumex
        ssy[i] = sumey
        sst[i] = sumet

    return ww, ssx, ssy, sst


# 计算四种情况
params = [(12, 0), (12, 0.5), (16, 0), (16, 0.5)]
results = []
for ntp_val, cep1_val in params:
    ww, ssx, ssy, sst = calculate_spectrum(ntp_val, cep1_val)
    results.append((ww, ssx, ssy, sst))

# 绘制四张图
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

for i, (ww, ssx, ssy, sst) in enumerate(results):
    label = f"ntp={params[i][0]}, cep1={params[i][1]}"
    axes[i].plot(ww * 0.056 / 375, np.abs(ssx), label=f'{label} - Re(ssx)')
    axes[i].plot(ww * 0.056 / 375, np.imag(ssx), label=f'{label} - Im(ssx)')
    axes[i].set_xlabel('Frequency')
    axes[i].set_ylabel('Spectral Intensity')
    axes[i].set_title(f'Spectrum for {label}')
    axes[i].legend()
    axes[i].grid(True)

plt.tight_layout()
plt.show()
