# Program untuk mencari nilai maksimum dari masalah optimasi dengan metode simpleks

import numpy as np 
import tabulate  
from termcolor import colored  

class SimpleksSolver:
    # Kelas ini mengatur semua perhitungan metode simpleks
    def __init__(self, c, A_ub, b_ub):
        self.c = c 
        self.A_ub = np.array(A_ub)  
        self.b_ub = np.array(b_ub)  
        self.n_vars = len(c)  
        self.n_constraints = len(b_ub) 
        
        # Menyimpan nama-nama variabel
        self.variabel_basis = ['Z'] + [f'S{i+1}' for i in range(self.n_constraints)]
        
        self.buat_tabel_simpleks_awal()
    
    # Membuat tabel awal untuk perhitungan
    def buat_tabel_simpleks_awal(self):
        slack_matrix = np.eye(self.n_constraints)
        
        self.tabel = np.zeros((self.n_constraints + 1, 
                                self.n_vars + self.n_constraints + 1))
        
        self.tabel[:-1, :self.n_vars] = self.A_ub
        self.tabel[:-1, self.n_vars:self.n_vars+self.n_constraints] = slack_matrix
        self.tabel[:-1, -1] = self.b_ub
        
        self.tabel[-1, :self.n_vars] = [-x for x in self.c]
    
    # Menampilkan tabel ke layar
    def tampilkan_tabel(self, iterasi, judul=None, ev=None, lv=None, pivot=None):
        if ev is not None and lv is not None and pivot is not None:
            print(colored(f"Entering Variable (EV): {ev}", 'green'))
            print(colored(f"Leaving Variable (LV): {lv}", 'red'))
            print(colored(f"Pivot: {pivot}", 'yellow'))
        
        if judul:
            print(colored(f"\n{judul}", 'cyan', attrs=['bold', 'underline']))
        else:
            print(colored(f"\n=== Iterasi {iterasi} ===", 'cyan', attrs=['bold']))
        
        headers = ['Variabel Basis'] + ['Z'] + [f'X{i+1}' for i in range(self.n_vars)] + [f'S{i+1}' for i in range(self.n_constraints)] + ['RHS']
        
        data_tabel = []
        baris_z = [
            self.variabel_basis[0],  
            1,  
            *self.tabel[-1, :self.n_vars+self.n_constraints], 
            self.tabel[-1, -1] 
        ]
        data_tabel.append(baris_z)
        
        for i in range(self.n_constraints):
            baris = [
                self.variabel_basis[i+1],  
                0, 
                *self.tabel[i, :self.n_vars+self.n_constraints], 
                self.tabel[i, -1] 
            ]
            data_tabel.append(baris)
        
        print(tabulate.tabulate(
            data_tabel, 
            headers=headers, 
            tablefmt='fancy_grid', 
            numalign='center', 
            stralign='center'
        ))
    
    # Mencari kolom untuk perhitungan berikutnya
    def cari_kolom_pivot(self):
        kolom_masuk = np.argmin(self.tabel[-1, :-1])
        ev = f'X{kolom_masuk + 1}' if kolom_masuk < self.n_vars else f'S{kolom_masuk - self.n_vars + 1}'
        return kolom_masuk, ev

    # Mencari baris untuk perhitungan berikutnya
    def cari_baris_pivot(self, kolom_masuk):
        rasio = []
        for i in range(self.n_constraints):
            if self.tabel[i, kolom_masuk] > 0:
                rasio.append(self.tabel[i, -1] / self.tabel[i, kolom_masuk])
            else:
                rasio.append(float('inf'))
        baris_keluar = np.argmin(rasio)
        lv = self.variabel_basis[baris_keluar + 1]
        return baris_keluar, lv

    # Melakukan perhitungan sampai mendapat hasil akhir
    def iterasi_simpleks(self):
        self.tampilkan_tabel(0, "Tablo Simpleks Awal")
        iterasi = 1
        
        while np.any(self.tabel[-1, :-1] < 0):
            kolom_pivot, ev = self.cari_kolom_pivot()
            baris_pivot, lv = self.cari_baris_pivot(kolom_pivot)
            pivot = self.tabel[baris_pivot, kolom_pivot]
            self.pivot(baris_pivot, kolom_pivot)
            self.tampilkan_tabel(iterasi, ev=ev, lv=lv, pivot=pivot)
            iterasi += 1
        
        print(colored(f"\nKarena pada iterasi {iterasi-1} semua nilai pada baris fungsi tujuan sudah non negatif, maka penyelesaian optimal telah tercapai.", 'red'))
        return self.tabel

    # Mengubah nilai-nilai dalam tabel
    def pivot(self, baris_pivot, kolom_pivot):
        pivot = self.tabel[baris_pivot, kolom_pivot]
        self.tabel[baris_pivot] /= pivot
        for i in range(self.tabel.shape[0]):
            if i != baris_pivot:
                faktor = self.tabel[i, kolom_pivot]
                self.tabel[i] -= faktor * self.tabel[baris_pivot]
        var_masuk = f'X{kolom_pivot + 1}' if kolom_pivot < self.n_vars else f'S{kolom_pivot - self.n_vars + 1}'
        self.variabel_basis[baris_pivot+1] = var_masuk

# Meminta input dari pengguna dan menjalankan perhitungan
def solve_linear_programming():
    print(colored("=== Program Linear Programming Metode Simpleks (Maksimasi) ===", 'cyan', attrs=['bold']))
    n_vars = int(input("Masukkan jumlah variabel: "))
    c = [int(float(input(f"Koefisien x{i+1}: "))) for i in range(n_vars)]

    n_constraints = int(input("Masukkan jumlah kendala: "))
    A_ub = []
    b_ub = []
    for i in range(n_constraints):
        print(f"\nKendala {i+1}:")
        A_ub.append([int(float(input(f"Koefisien x{j+1}: "))) for j in range(n_vars)])
        b_ub.append(int(float(input("Batas kanan kendala: "))))

    solver = SimpleksSolver(c, A_ub, b_ub)
    tabel_optimal = solver.iterasi_simpleks()

    # Menampilkan hasil
    print(colored("\n=== Solusi Optimal ===", 'green', attrs=['bold']))
    print(colored("Nilai Optimum:", 'yellow'), int(tabel_optimal[-1, -1]))
    
    # Menampilkan nilai x1, x2, dst
    variabel = []
    for i in range(solver.n_vars + solver.n_constraints):
        kolom = tabel_optimal[:, i]
        if np.sum(kolom == 1) == 1 and np.sum(kolom == 0) == len(kolom) - 1:
            baris = np.argmax(kolom == 1)
            if i < solver.n_vars:
                print(colored(f"{colored('x' + str(i+1), 'yellow')} = {int(tabel_optimal[baris, -1])}", 'white'))

# Program utama
def main():
    while True:
        solve_linear_programming()
        if input("\nApakah Anda ingin menyelesaikan masalah lain? (y/n): ").lower() != 'y':
            break
    print(colored("Terima kasih telah menggunakan program!", 'cyan', attrs=['bold']))

if __name__ == "__main__":
    main()