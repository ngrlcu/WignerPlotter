import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from qutip import *

st.set_page_config(layout="wide")

dim=40

def make_squeezing(key):
    with st.sidebar.expander("SQUEEZING CONTROLS"):
        r = st.slider("r", min_value=0., max_value=2., value=0., step=0.5, key=key)
        theta = st.slider("theta (•π)", min_value=-2., max_value=2., value=0., step=0.1, key=key)
    s = r*(np.cos(theta*np.pi) + np.sin(theta*np.pi)*1j)
    return s

def make_displacement(key):
    with st.sidebar.expander("DISPLACEMENT CONTROLS"):
        x = st.slider("Re{β}", min_value=-5., max_value=5., value=0., step=0.2, key=key)
        y = st.slider("Im{β}", min_value=-5., max_value=5., value=0., step=0.2, key=key)
    return x+y*1j

def make_photon_menu(key=0):
    MENU = ('vacuum', 'thermal', 'coherent', 'fock')
    photon_type_option = st.sidebar.selectbox("", MENU, key=key)

    if photon_type_option == "vacuum":
        s = make_squeezing(key)
        d = make_displacement(key)
        return displace(dim, d) * squeeze(dim, s) * basis(dim, 0)

    elif photon_type_option == "thermal":
        N = st.sidebar.slider("Mean number", min_value=0., max_value=5., value=0., step=0.5, key=key)
        s = make_squeezing(key)
        d = make_displacement(key)
        return displace(dim, d) * squeeze(dim, s) * thermal_dm(dim, N)
        
    elif photon_type_option == "coherent":
        x = st.sidebar.slider("Re{α}", min_value=-5., max_value=5., value=0., step=0.2, key=key)
        y = st.sidebar.slider("Im{α}", min_value=-5., max_value=5., value=0., step=0.2, key=key)
        s = make_squeezing(key)
        d = make_displacement(key)
        return displace(dim, d) * squeeze(dim, s) * coherent(dim, x+y*1.j)

    elif photon_type_option == "fock":
        n = st.sidebar.slider("n", min_value=0, max_value=5, value=1, step=1, key=key)
        s = make_squeezing(key)
        d = make_displacement(key)
        return displace(dim, d) * squeeze(dim, s) * fock(dim,n)
        
    else:
        print("Error: making the sidebar failed!")
        return -1

def make_sup_or_mix_menu(key=0):
    sup_or_mix = st.sidebar.radio("", ["Superposition", "Mixture"], 1, key=key)
    if sup_or_mix == "Superposition":
        sup = True
        mix = False
    else:
        sup = False
        mix = True
    return sup, mix

def make_superposition(psi_old, superposition=False, key=0):
    if superposition:
        key+=1
        psi_new = make_photon_menu(key)
        psi_sup = psi_old + psi_new
        superposition = st.sidebar.checkbox("Superposition", False, key=key)
        psi = make_superposition(psi_sup, superposition, key).unit()
    else: psi = psi_old
    return psi

def make_mixture(psi_old, mixture=False, key=0):
    if mixture:
        key+=1
        psi_new = ket2dm(make_photon_menu(key))
        if psi_old.type is not "oper":
            psi_old = ket2dm(psi_old)
        psi_mix = psi_old + psi_new
        mixture = st.sidebar.checkbox("Mixture", False, key=key)
        psi = make_mixture(psi_mix, mixture, key)
    else: psi = psi_old
    return psi.unit()
    
def wignerplot(psi):
    fig = plt.figure(figsize=(17, 8))
    
    ax = fig.add_subplot(1, 2, 1)
    plot_wigner(psi, fig=fig, ax=ax, alpha_max=5)
    ax.set_title(None)
    ax = fig.add_subplot(1, 2, 2, projection='3d')
    plot_wigner(psi, fig=fig, ax=ax, projection='3d', alpha_max=5)
    ax.set_title(None)
    plt.close(fig)
    return fig

#--- SIDEBAR ---
psi = make_photon_menu()

sup, mix = make_sup_or_mix_menu()
psi = make_superposition(psi, sup)
psi = make_mixture(psi, mix)
    
#--- HEAD ---

st.title("Wigner Function Plotter")

#--- PLOT ---

with st.spinner(text='Plotting...'):
    st.pyplot(wignerplot(psi), use_container_width=True)
