import warnings
import pandas as pd

# Специально вызываем предупреждение
warnings.warn("Тестовый DeprecationWarning", DeprecationWarning)
warnings.warn("Тестовый FutureWarning", FutureWarning)

# Провоцируем классическое предупреждение pandas (если версия 1.5.3)
df = pd.DataFrame({'A': [1, 2, 3]})
# Попытка создать цепочку присваиваний (часто вызывает SettingWithCopyWarning)
df[df['A'] > 1]['A'] = 5