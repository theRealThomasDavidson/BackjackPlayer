import matplotlib.pyplot as plt
import json



def main():
    data = json.loads(open("400deckspayouts.json").read())
    data = data["payoutlists"]
    print("start")
    plt.hist(data, bins=50, range=(0., 2.5))
    plt.show()
    print("end")

if __name__ == "__main__":
    main()