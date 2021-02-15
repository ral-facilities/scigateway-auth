with open("test/keys/jwt-key", "r") as f:
    PRIVATE_KEY = f.read()

with open("test/keys/jwt-key.pub", "r") as f:
    PUBLIC_KEY = f.read()
VALID_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6dHJ1ZSwiZXhwIjo5OTk5OTk5OTk5fQ.L2pR4ViBiUoZtEYat8boDyfs1RgVbHQS_-MNK7-QfdA4aEzfghJjm53EeySw88zyVpiZcNgO9owu400ywPDmKu0A88i82hhltEd0zIPLd3PfCUUe4NlzZ5aNavuemrQ3FAztc9c0GIJFVBwPkItLmwyL47uTgSBJB_a5y51tVh61g_FLg3Bb7vYwyTyjxIUhrzwc4mXfpeybQae5fcQKJzE3MbZxHEtGYhL9p7ukaaFl1UnGeGba_CALD3kZBLFge50eobiDUx_RTpUHHRrOq4prtiBXZk7LH1xrBIVhEXqJX04aoS-0N7cxtJ5RUcOzLYKNAHo0eBVjIj6cly7aaz_DDEIjDQb51FvvwQBXBN33XOikABrI6wjkIT9wox7Vlh605e5VjyqlPI1UdHDpvW2yISxpF0_c8wfLQF5yotw9ETlmwSPyr_nA4BlpUFg7YxyOLOcF8DlB7-egQuUSLHm3FGi18dIIrPFZaIF0YjlZysLNdGxSqHzMMyLzQ1kDh8IDoJD8ylKvw8ElKHg7gs9j620J-hKBI8fdfISMEtU9-U05lNuT9wpP0Z3QcjgeoXiEtqYZN7mkD3DJVzCq4SB3oRWupo5gmrHEq_z7ElYHN4aO4cOJxw_kgFuiNjLqTFTp08C8lUkcsOYB5ZPHUYnmFqGk6XARe_9KJkjLV5I"
INVALID_ACCESS_TOKEN = VALID_ACCESS_TOKEN + '1'
VALID_NON_ADMIN_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6OTk5OTk5OTk5OX0.ZrvLcWueXfix-dOtuFWdpZuUZAM8WrhtqUffEfZhLJPDbCe-I_D3Bcikznhtkb1k8-Kcj9MiLdUcaFXT-SvyYpc_c2Zj690FMVqfrR9yjaGGWG-2Lx2izedjSFoNu7zT779hmDanzTFNtLzSZeSU8GhXXSsrzgY2FwcDMNHiCcKb6JlcsrmSRIKQCiKK4k_VadJ7e7EioCN9tVAGiORwOy81r1m5RqSui6y8SvYzTFXSbDwjTErTVUfdIsUcN9_i_WEMn1sPztVPeQ_0o3sW0XsIxK-peuiqAqnX67OQpNQtUoMd_RtY603U9zdGujCDW-zYz-vIzWhUu5GNyFaA_1zJIuS-Ga3gGS-QXrLTYrosBTCpK0OCZp8mM4Guue7obKa5zeEL-Cq2-WlrLuPMlxCPrPH1qu_pMtYO-yaMIrfX6Xt7g-0p2ZQVIaR-vesXJC6MTIO-bqq8rIv7ToImf774gY2Fg5EiNnhkJAml8AaKfSynWsRoV7YsXoCnlqGLCwE4-RyRoq-rmm4ms1zEzwl38ydPWUzNqQMTkwqj5eYsRw-ncfVssnP0VcZ5HCcHIXKHOVuHrxqc5wJg-MkhCfJazOb8pjyDZg6fW4Omsr54Rthz3R7jeska0AbinZzAlPJSwdx9ouPxvdAD2hWxAPnp9Ii16gn50V38eMLm3wA"
EXPIRED_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6MTU3ODQ0MTU5OX0.cZh9eezkKpuUhx49NQORXm9Nq6VaMNA9hI_XtRlwr9wO2RkX6g4DE0I9ls9QDp8mNs1ZrKolM1aAa-3xi6GiHQBK9hQFSVZK8UYd_wG4AbnuBUmWypSKB3AD_fUtNeCv1NxOdKQPbx6CgKguWN3DmjAFrc84nrrX-FHGx5IsmiD_TeSudqBHiG7Kqbn4FWhVmyzcwTs4d0eCtTpJNGaLcNNp5WuR8GX0CnCZdgM6eFM8pvoAZGJ_lXEQ3ayCY-4CShWinAa2G1x_mwgd0-y5KhmjU1DdY6G0qqlmeFBO4Qz6LSoEjp5KHiSTSRNLVr9FIHYJY5v2MhZ9Jt-bp3e7mDEyR8M8RtnVRGAtn_KKovh0e5v2AgFnUsOVYtj3g_gr5lbiwpVY9cNa24HJqPxSb9WnjBLWYHcyhLCZKDTtZ0xdCDeQrO772rCpfb2tSif6LijQJRuhJzvjdcHJgZNeFDoF0bGha_brqRqOo4ayIn-BrfuBmN4ShplLs_Q_vGg76do7Px1QVc4_1mrXgIdl9xDCtv-z80E7Y6LzEPtEGwfoyqLJWhyF5HRYIUgJSakK6ZtZsFGMIC3uCCMZGD5KZDUcc_UKZOIZZ9mlDXyPkIehZ1AoQszZKJbkvoDf9xYLQLpdf7-0vIIhqqaIM2VjOmKD-BQjUvrfyd-Olv_sPAw"
REFRESHED_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6dHJ1ZSwiZXhwIjoxNTc4NDQxOTAwfQ.BlwipnOq1Au2IhzRdExiJc9UN8iQ1w9tAAxX2NEZicNoAazGBj7V4YLrDIQJIlnd3e1RUjlQzyb9P1aw4WOLwilZIoNCRHqGZxYwy1qZIrEyhGqdI545k-QKG1hlXc1xK9A6eOopNWtrFd1gvxELHgdNihTPGEbcGGO_NRoXs89KZpFgdmEd_GxsYksGCO5f1UTHbkptZ2zoYso9gLcWRpUX7j27I2EgNdbYkQ9DIglYWnLkEIzvVhE96CQzn_Pea7X1GHTWsLYD5jpFobwM8wc-F_e_UhV375cXH36N41f12_RmTbO5WVV0luLSeKHZCLyqpVCdrOM0hL5ERVdvtRx6TJSF_nrt84ewwtt1XeAQYY_InPaobN4xvUxpF7jW-FmaV-WVIv8D8qDRTtmRisyJjRHlDopRHWnfHe1oV-32_y27VcVRXqUn-GQudRqteTG6ngY1jaREvZLFANGzrvwEFKBLaKGkljt9KFQ7QuknXXbjKSmitcxfps6RNVjAJALxi-aEinKC3d7fgVm09Sg6X_tG0funABIzENQwSGtTCZYfcnryL7D4V0mU8BuviLQbmA9yRmIOZjHfBYzTEA3MySe3fPGPj8Z5a8Z2jqbXpub7pT2RsNIxD4SqijoZBnO4ZmPMiBkUoTXaq8v2Rk2Q97oepqKkl85xb6G4tX8"
REFRESHED_NON_ADMIN_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6MTU3ODQ0MTkwMH0.ew2pVkjd1YD3gha-kjw50lrtqMyhxZZT6nwYzQXM7PfjykjvhJRWS6wUXeYSeT8lGwLLZDXdaLY3nCMM8UK6ERckIvte2-BFFx12h4ZktWMLcN0tSRaKJU6mp3wrHTlVQ-iEQOtQ1GOYeZdryGbjotrq3IdRY2iuOpmTGqSRhSuAO262BEPpUxm-bgUqE9V7j9lnSRBA_GZ0OPssxOmnKrXqVoyi3zmrAcWf-Ci409JPmdrczPy6dBABHt8ayuqtY3nc8jtB45N9o97_mvfbeP2Vsf4ndFt7i5mOhib1Ytgj_TZaB1_aErBBk3VAq9uKgb9EIEJSFFj2es_kMjmCkPKRP-Bpm_caIp5Agopoocg6vc4iUnRRpJGPWSJNcBeWDoI_8aC03MME9gIuqrCRdeXJyjRRl4pEDkdi2QchV2rm1miD6uRy-ho4jBGydiylA-yZCPexnyT13Pxom63c2WqX0muHTHGD3kMCkoO0RN_aF2s5kkKkvVrRHuk2_MNg1KX03mZ1jMp3y6KNHXJuY6REZqUtufVvVNxjx-AZJajw2EkmfTMCtldtAwc54EL-i7rFc9CmIbiXFsEZK1oKyj8WOqLtN_b-DVdrzx5D6s7SNlDu9ahhdzSII2CL3_QzJNJlOiCI3dfp73L9CmMZoPz5CJiRxnwzOfitVScoOX4"
NEW_REFRESH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjE1NzkwNDY0MDB9.pAQEve08F-fDXHZO4YeHziqO9MesmISs2LRZUTUGJHBCoJcB5tTpSgHq-XMhKkA4iVPmsN1sQ5rD6Ahr9wvKLQLTqMgDf-Gc7AVIDZ79I1D74o1wDUMEC5WUll9sUtcUuImAl2KQHWK-i74uOkZGv7ibzGZFMREoW9KApA9yCc15KeZgSF9XoKxyAkr2T1WYH2kzT9DRUn5ddZgjDJHjlJhUuZUSdDqAXKT4dYZabP48xZmjSBrnr7MdoS5x2jhmanBIWFtbuuAK1L9MRd0uY1RAcrueUjoDEfjoT56R9nju4rcRL5QGaArJSQpNEel-mxqHqEZpjE3Me1AGjUFT494v95Rg2KG2aFGIfxcMMaEd5dNU2BlhGlviQK5KDuLuBULra_0aiFm8TRVHjTWE9uIKI0ZS5Vzl4umu3c1YAbWXAolBxXoH8tYnuvVYI-HCdwd7f_B1BPrAmPBhSRLaBrQwqU_EJtit5XSi9Pm4Y-c93EmzT0sFZk9Z8-xjw0Sr2hbNwGsd5gSN_YPUZH-r9XZ6xy1a9HRVKS0UVWq2P5oSHtrafl95OZ_WbSd4Hh0cOnuf6chz4AWM6JP-tlOYMas5D387a9el0Pl3nl3xO9pk7oUATeeMlm1Vx2nt7bvsbgQwBhfY5OnGrW9reem1zZTEm4SpJTraKLleGh1UGd8"
VALID_REFRESH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk5OTk5OTk5OTl9.dgakoOk09sfdjTpPvC28RQbmJFt_F2eWq4AuBGyp9Z6ri1XHycRNiv-4ewixw_uZaD57Y_Xr5tJuoSlUEfVL0f2R-X-AHhGb1aYsY6Gk0hIBupYkLM-sEOQNLGffK7ayd58k8ay_GtjxuLcmsqqBdCWYM3nr0JCDpsnBYaRXFvHQKThOk7BEJPFmlEk06w0C8OW35GDn9EPl_ArKKyUDm2H1Wbgjn7mVrVmpcoUyXmaDMJ63ZOMvm82j-3y2H2Bye0Ezlc2h4DLPH9KB3CuwdArwaka_ybA8_DVah4poWvZXxS3vNS5cLBGnKPwRSjo4VHcgilpqeM63nrelfqjEg2MP5-CDnUro0MrtoHg1VoF0zLTFuDrdx4YkD---uML0e3K8_UhCG1ipj-WwA9oUpQ0SEZ8KnlNKXRxutuyei3U7Q9c60Joye7sldmAVWDL6W8EnUPyGKAYyMSWDbzHANzHCAaBl5GJSuiiHFyjVli9PFJJPcwJb4hXZybjaPNsmeiHnZUPCY_ESuyFQYJpo4Ot5rbYabBkVVvTz5BK3RXVAwecxEGrzsRyl_vLOKn_D1T6_gQkHmPI99ySDNIo7qL7N9P5aLxwJTGYl9xczsQtuUXe1PurjQSj78b4ioU8ImPC1AYwGJzRHDgeM3q04nx3tFPOwLmOdRZwEBmcGXWk"
EXPIRED_REFRESH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjEwMDAwMDAwMDB9.SWuznEIymHglPP4rSNjlVjY5kAwNKQEgiVsXxItxCgrdhNCrhadKLYTV0EFs3oEfylCSpkrQF1nfhlXhOhuUVvWQJR6itxVDxMfyS_YkDSLyrdeiEbpYcQ-dNv7mPKdPOdcwqnh_f0w5Fg961zoGAYLxpdCN67hvIkW1RXMX4n8ZGV_kQ9vdLpg3Jx4x29iSzAKF5ZBdocwUZZaYojpVdsIvv3cdoxS0LRShgKowYwdyKp8xWVacV8wS4stUh9rpk70MSVjlec4ecAaDqMxI0WyO3bVxtXsKj9bGlbzyUvhxEMRFyuyYtpMIXspuvblqqDJZkCiMqbrJxtJxXirNzwJYqKwgsjJxzrcsJygWi4GnVUykaOvvIznZ9iJmaVsMFrXDjLhQDxsoRAQuodpHdE4tWzpXWSQgMLHscjvFqfIgybX0JQCeOXMtXVgIj3Y8a2MvsmEYMmqwypYyRLrF4LsjTi9A9vu3Zo5RU5Lbwqbwvp-Auan-_4Ef5aBKgYCa1CaMP-nRZMMz8esdeEwx_xQ21FX1zZt-VMt-bC_J-b_9Ym7gpizvi-nrymF-yNLS8HF519NM1TlV0H_4Kc4uI6WESlGcM9TyEMh8yoy2tMMzURyahy8h98hIG5H0sP1fadZ_RdYxhqR79VDISxugVcXmdltMlMRmFrRSwf1ENXk"
ACCESS_TOKEN_WITHOUT_ADMIN_INFO = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJleHAiOjk5OTk5OTk5OTl9.beDpd6SrucSThtzszb1sfr4xieVpWzoZ7uVRj6vOeIy-MI0yAfn7M-PnDOdZoyOMJbGEP_BWNo3e4zpiyv9wxx-TVL_EKccdre92seYPFI8pOnAm0OlmbM9hOwSSQuhAuqSAzxSupU0V2CPXN9YG_xOFFhrpAgNIltyqcpkv0VArxYbniJtGEJt_WTwn15XO1oEDK7-3w7CNidQ2_BUrp0ZfYDVjgJXpaK6-op_7KLUBqXzZtAIbf2Z97O05sZk5Iv0citk9Mqh3a17CUajNDJAQAwBuUomwIvqm0flB3SriEfrUx7tteNlH8ziZ1Vs3b9Dg6hjvF0jDkC8BL2LZoI6eYP7iVIyS-ZwGEjnE9qiBqblP9E4ENVygCfP7A1SDG8XsCmkIt1lXFKM8qgjfPaompOI8rY5mJEwgbZTJmDCPpzJ9ethJmpuZbuDOQYjI1occkIeeOkzJsHnm3vkv4TTZPgifckUlIJdXaDFGGLZYC05cMFB2x-DdOQuzX1Dvr4OAKQH_g5vEibXhH3amMqRBNlHZlmc0WundBmo5hJFSUvR7oWa0nprWk1iPUlMuijyedTyVk51tJqVe1orDg2W2yp7ehdgAWJiWAwOpYL4Tbj-rypOq12tqnemaS5eykG0Ybo7fNG_4hTbTiX4SsPIhEusVte7-y-vpNVbwefE"
MAINTENANCE_CONFIG_PATH = "path/to/config/test_config.json"
MAINTENANCE_STATE = {"test": "test"}