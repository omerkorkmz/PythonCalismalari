class HesapMakinesi:
    def __init__(self):
        pass

    def hesapla(self):
        a = int(input("sayi1: "))
        b = int(input("sayi2: "))
        while True:
            secenek = int(input("1-topla\n2-cikar\n3-carp\n4-bol\nSeçiminiz: "))

            match secenek:
                case 1:
                    print(a + b)
                    break
                case 2:
                    print(a - b)
                    break
                case 3:
                    print(a * b)
                    break
                case 4:
                    print(a / b)
                    break
                case _:
                    print("Geçersiz seçenek. Lütfen tekrar deneyin.")

if __name__ == "__main__":
    hesap_makinesi = HesapMakinesi()
    hesap_makinesi.hesapla()