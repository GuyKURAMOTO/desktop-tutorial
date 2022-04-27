export class Card {
    public static readonly SUSPECT = new Card('suspect', '犯人', false);
    public static readonly DETECTIVE = new Card('ditective', '探偵', true);
    public static readonly ARIBI = new Card('aribi', 'アリバイ', false);
    public static readonly TRADE = new Card('trade', '取引', true);
    public static readonly MANIPULATION = new Card('manipulation', '情報操作', false);
    public static readonly RUMOR = new Card('rumor', 'うわさ', false);
    public static readonly BOY = new Card('boy', '少年', true);
    public static readonly DOG = new Card('dog', 'いぬ', true);
    public static readonly WITNESS = new Card('witness', '目撃者', true);
    public static readonly CITIZEN = new Card('citizen', '市民', false);
    public static readonly DISCOVERER = new Card('discoverer', '第一発見者', false);
    public static readonly CONSPIRE = new Card('conspire', 'たくらみ', false);
    private constructor(public readonly kind: string, public readonly name: string, public readonly targeting: boolean) { }
}
