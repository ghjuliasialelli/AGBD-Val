"""Spanish single-tree ABOVE-GROUND biomass equations, by IFN species code.

Source: the NFI's own INIA models — Ruiz-Peinado, del Rio & Montero 2011 (softwoods, Forest Systems
20:176) and Ruiz-Peinado, Montero & del Rio 2012 (hardwoods, Forest Systems 21:42), the published
refinement of Montero, Ruiz-Peinado & Munoz 2005 (Monografia INIA 13) used for Spanish NFI carbon
reporting. Coefficients transcribed from the two open-access papers' tables.

Units: W in kg (oven-dry), d = dbh in cm, h = total height in m. Above-ground total =
Ws (stem) + Wb7 (thick branches >7cm) + Wb2_7 (medium 2-7cm) + Wb2 (thin <2cm + leaves/needles).
The below-ground root term Wr is DELIBERATELY EXCLUDED (this is AGB, not total). A few species give a
combined Ws+Wb7 term (Q. pyrenaica, E. globulus) — not double-counted. Z is a threshold switch: a thick-
branch term applies only above a diameter cut (e.g. d>37.5 cm). Components are clipped at >=0 (a few
linear terms go slightly negative for small trees). Vectorised over numpy arrays.
"""
from __future__ import annotations
import numpy as np


def _z(d, thr, expr):
    """Threshold-switched term: expr where d>thr, else 0."""
    return np.where(d > thr, expr, 0.0)


def _agb(code, d, h):
    d = np.asarray(d, float); h = np.asarray(h, float)
    d2 = d * d
    c = str(code).zfill(3)
    if c == "021":  # Pinus sylvestris
        return (0.0154*d2*h + _z(d, 37.5, 0.540*(d-37.5)**2 - 0.0119*(d-37.5)**2*h)
                + 0.0295*d**2.742*h**-0.899 + 0.530*d**2.199*h**-1.153)
    if c == "022":  # Pinus uncinata
        return 0.0203*d2*h + 0.0379*d2 + (2.740*d - 2.641*h)
    if c == "023":  # Pinus pinea
        return (0.0224*d**1.923*h**1.0193 + _z(d, 22.5, 0.247*(d-22.5)**2)
                + 0.0525*d2 + (21.927 + 0.0707*d2 - 2.827*h))
    if c == "024":  # Pinus halepensis
        return (0.0139*d2*h + _z(d, 27.5, 3.926*(d-27.5))
                + (4.257 + 0.00506*d2*h - 0.0722*d*h) + (6.197 + 0.00932*d2*h - 0.0686*d*h))
    if c == "025":  # Pinus nigra
        return 0.0403*d**1.838*h**0.945 + _z(d, 32.5, 0.228*(d-32.5)**2) + 0.0521*d2 + 0.0720*d2
    if c == "026":  # Pinus pinaster
        return 0.0278*d**2.115*h**0.618 + 0.000381*d**3.141 + 0.0129*d**2.320
    if c == "027":  # Pinus canariensis
        return (0.0249*(d2*h)**0.975 + _z(d, 32.5, 0.634*(d-32.5)**2)
                + 0.00162*d2*h + (0.0844*d2 - 0.0731*h*h))
    if c == "031":  # Abies alba
        return 0.0189*d2*h + 0.0584*d2 + (0.0371*d2 + 0.968*h)
    if c == "032":  # Abies pinsapo
        return (0.00960*d2*h + _z(d, 32.5, 1.637*(d-32.5)**2 - 0.0719*(d-32.5)**2*h)
                + 0.00344*d2*h + 0.131*d*h)
    if c == "038":  # Juniperus thurifera
        return (0.0132*d2*h + 0.217*d*h + _z(d, 22.5, 0.107*(d-22.5)**2)
                + 0.00792*d2*h + 0.273*d*h)
    if c == "043":  # Quercus pyrenaica (Ws+Wb7 combined)
        return 0.0261*d2*h + (-0.0260*d2 + 0.536*h + 0.00538*d2*h) + (0.898*d - 0.445*h)
    if c == "044":  # Quercus faginea
        return 0.154*d2 + 0.0861*d2 + (0.127*d2 - 0.00598*d2*h) + (0.0726*d2 - 0.00275*d2*h)
    if c == "045":  # Quercus ilex
        return 0.143*d2 + _z(d, 12.5, 0.0684*(d-12.5)**2*h) + 0.0898*d2 + 0.0824*d2
    if c == "046":  # Quercus suber (cork oak)
        return (0.00525*d2*h + 0.278*d*h) + 0.0135*d2*h + 0.127*d*h + 0.0463*d*h
    if c == "047":  # Quercus canariensis
        return 0.0126*d2*h + 0.103*d2 + 0.167*d*h
    if c == "054":  # Alnus glutinosa
        return 0.0191*d2*h + 0.0512*d2 + 0.0567*d*h
    if c == "055":  # Fraxinus angustifolia
        return 0.0296*d2*h + _z(d, 12.5, 0.231*(d-12.5)**2) + 0.0925*d2 + 2.005*d
    if c in ("058", "258"):  # Populus x euramericana
        return (0.0130*d2*h + _z(d, 22.5, 0.538*(d-22.5)**2 - 0.0130*(d-22.5)**2*h)
                + 0.0385*d2 + (0.0774*d2 - 0.00198*d2*h))
    if c == "061":  # Eucalyptus globulus (Ws+b7 combined; no root)
        return 0.0221*d2*h + 0.154*d**1.668 + 0.180*(d2*h)**0.587
    if c == "066":  # Olea europaea
        return 0.0114*d2*h + 0.0108*d2*h + 1.672*d + (0.0354*d2 + 1.187*h)
    if c == "067":  # Ceratonia siliqua
        return 0.142*d**1.974 + 0.104*d2 + 0.0538*d2 + (0.151*d2 - 0.00740*d2*h)
    if c == "071":  # Fagus sylvatica
        return (0.0676*d2 + 0.0182*d2*h + _z(d, 22.5, 0.830*(d-22.5)**2 - 0.0248*(d-22.5)**2*h)
                + 0.0792*d2 + (0.0930*d2 - 0.00226*d2*h))
    if c == "072":  # Castanea sativa
        return 0.0142*d2*h + _z(d, 12.5, 0.223*(d-12.5)**2) + 0.230*d*h + 0.221*d*h
    return None  # no published INIA equation for this code


COVERED = {"021", "022", "023", "024", "025", "026", "027", "031", "032", "038", "043", "044", "045",
           "046", "047", "054", "055", "058", "258", "061", "066", "067", "071", "072"}


def agb_kg(code, d_cm, h_m):
    """Total above-ground biomass [kg]; None if the species code has no INIA equation."""
    r = _agb(code, d_cm, h_m)
    return None if r is None else np.clip(r, 0.0, None)
