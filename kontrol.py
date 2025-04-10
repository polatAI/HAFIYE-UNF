class GeriTakipKontrol:
    def __init__(self, takipciler_dosya="takipciler.txt", takip_edilenler_dosya="takip_edilenler.txt"):
        self.takipciler_dosya = takipciler_dosya
        self.takip_edilenler_dosya = takip_edilenler_dosya
        self.takipciler = set()
        self.takip_edilenler = set()
        self.geri_takip_etmeyenler = set()

    def dosyalari_oku(self):
        with open(self.takipciler_dosya, "r", encoding="utf-8") as f1:
            self.takipciler = set(line.strip() for line in f1 if line.strip())

        with open(self.takip_edilenler_dosya, "r", encoding="utf-8") as f2:
            self.takip_edilenler = set(line.strip() for line in f2 if line.strip())

    def geri_takip_edenleri_bul(self):
        self.geri_takip_etmeyenler = self.takip_edilenler - self.takipciler

    def dosyaya_yaz(self, cikti_dosyasi="geri_takip_edenler_degil.txt"):
        with open(cikti_dosyasi, "w", encoding="utf-8") as f_out:
            for user in sorted(self.geri_takip_etmeyenler):
                f_out.write(user + "\n")
        print(f"{len(self.geri_takip_etmeyenler)} kişi seni geri takip etmiyor.")

    def calistir(self):
        self.dosyalari_oku()
        self.geri_takip_edenleri_bul()
        self.dosyaya_yaz()
