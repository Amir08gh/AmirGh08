from itertools import combinations, product  
# برای تولید ترکیب‌ها و حاصل‌ضرب دکارتی استفاده می‌شود

# تبدیل لیست عددی minterms به لیست باینری با تعداد ثابتی از متغیرها
def decimal_to_binary(minterms, num_vars):
    return [format(m, f'0{num_vars}b') for m in minterms]

# مقایسه دو ترم باینری و بازگرداندن ترکیب آنها اگر فقط در یک بیت تفاوت داشته باشند
def compare_terms(term1, term2):
    diff_count = 0
    result = ''
    for a, b in zip(term1, term2):
        if a != b:
            result += '-'
            diff_count += 1
        else:
            result += a
    return result if diff_count == 1 else None  
# فقط اگر دقیقاً یک تفاوت دارند، ترکیب مجاز است

# ترکیب ترم‌ها با بررسی تفاوت یک‌بیتی بین هر جفت
def combine_terms(terms):
    combined = set() 
    # مجموعه ترم‌هایی که ترکیب شده‌اند
    used = set()    
    # ترم‌هایی که در ترکیب‌ها استفاده شده‌اند
    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            res = compare_terms(terms[i], terms[j])
            if res:
                combined.add(res)
                used.update([terms[i], terms[j]])
    leftovers = list(set(terms) - used) 
    # ترم‌هایی که ترکیب نشده‌اند
    return list(combined), leftovers

# پیدا کردن prime implicants با ترکیب مداوم ترم‌ها
def find_prime_implicants(minterms, num_vars):
    current_terms = decimal_to_binary(minterms, num_vars)
    all_combined = []
    while True:
        combined, unused = combine_terms(current_terms)
        all_combined.extend(unused)
        if not combined:
            break
        current_terms = combined
    all_combined.extend(current_terms)
    return list(set(all_combined)) 
# حذف موارد تکراری

# بررسی اینکه یک prime implicant کدام mintermها را پوشش می‌دهد
def get_covered_minterms(prime, minterms):
    return [m for m in minterms if all(p == '-' or p == b for p, b in zip(prime, format(m, f'0{len(prime)}b')))]

# گسترش prime implicantها به عبارات SOP با جایگزینی "-" با تمام ترکیب‌های ممکن
def expand_to_full_terms(primes, num_vars, variables):
    def expand_term(term):
        positions = [i for i, c in enumerate(term) if c == '-']
        combinations_list = list(product('01', repeat=len(positions)))
        expanded_terms = []
        for combo in combinations_list:
            term_list = list(term)
            for pos, val in zip(positions, combo):
                term_list[pos] = val
            expanded_terms.append(''.join(term_list))
        return expanded_terms

    full_expanded = []
    for prime in primes:
        binary_terms = expand_term(prime)
        for bterm in binary_terms:
            result = ''
            for i, c in enumerate(bterm):
                if c == '1':
                    result += variables[i]
                elif c == '0':
                    result += variables[i] + "'"
            full_expanded.append(result)
    return full_expanded

# پیدا کردن prime implicantهایی که ضروری هستند (essential)
def find_essential_primes(prime_implicants, minterms):
    chart = {m: [] for m in minterms}
    for p in prime_implicants:
        for m in get_covered_minterms(p, minterms):
            chart[m].append(p)
    essential = []
    for m, implicants in chart.items():
        if len(implicants) == 1 and implicants[0] not in essential:
            essential.append(implicants[0])
    return essential, chart

# پیدا کردن حداقل مجموعه‌ای از implicantها که تمام mintermها را پوشش دهند
def find_minimum_cover(prime_implicants, minterms, essentials, chart):
    uncovered = set(minterms)
    for p in essentials:
        uncovered -= set(get_covered_minterms(p, minterms))
    if not uncovered:
        return essentials
    remaining = [p for p in prime_implicants if p not in essentials]
    for r in range(1, len(remaining) + 1):
        for combo in combinations(remaining, r):
            cover = set()
            for p in combo:
                cover.update(get_covered_minterms(p, minterms))
            if uncovered <= cover:
                return essentials + list(combo)
    return essentials

# اجرای کل الگوریتم Quine-McCluskey
def quine_mccluskey(minterms, dontcares, variables):
    num_vars = len(variables)
    total_terms = sorted(set(minterms + dontcares))

    # بررسی شرایط خاص
    if not minterms:
        return "0"  
    # تابع همیشه صفر است
    if len(total_terms) == 2 ** num_vars:
        return "1"  
    # تابع همیشه یک است

    prime_implicants = find_prime_implicants(total_terms, num_vars)
    essentials, chart = find_essential_primes(prime_implicants, minterms)
    final_primes = find_minimum_cover(prime_implicants, minterms, essentials, chart)

    sop_terms = expand_to_full_terms(final_primes, num_vars, variables)
    return ' + '.join(sorted(sop_terms)) if sop_terms else "0"

# ------------------ main ------------------

if __name__ == "__main__":
    try:
        # دریافت تعداد متغیرها از کاربر
        num_vars = int(input("Tedad moteghayer ha ra vared kon (mesal: 3): "))
        
        # دریافت نام متغیرها (مثلاً ABC)
        variable_names = input(f"Horoof moteghayer ha ra vared kon (daghighan {num_vars} horoof mesal: ABC): ").strip().upper()
        if len(variable_names) != num_vars:
            raise ValueError(f"Tedad horoof moteghayer bayad daghighan {num_vars} ta bashad.")

        # دریافت mintermها و don't careها از کاربر
        minterm_input = input("Shomare-ye minterm ha ra ba fasele vared kon (mesal: 0 1 2 5): ").strip()
        dontcares_input = input("Shomare-ye don't care ha ra ba fasele vared kon (ya khali bezar): ").strip()

        try:
            minterms = list(map(int, minterm_input.split())) if minterm_input else []
            dontcares = list(map(int, dontcares_input.split())) if dontcares_input else []
        except ValueError:
            raise ValueError("Hame voroodi ha bayad adad sahih bashand.")

        # اعتبارسنجی: جلوگیری از تکرار
        if len(minterms) != len(set(minterms)):
            raise ValueError("Dar minterm ha adad tekrari vojood darad.")
        if len(dontcares) != len(set(dontcares)):
            raise ValueError("Dar don't care ha adad tekrari vojood darad.")
        if set(minterms) & set(dontcares):
            raise ValueError("Adad takrari dar minterm va don't care vojood darad.")

        # اجرای الگوریتم و نمایش خروجی
        result = quine_mccluskey(minterms, dontcares, variable_names)
        print("SOP (zarbdar jam):", result)

    except ValueError as ve:
        print("Khataye voroodi:", ve)