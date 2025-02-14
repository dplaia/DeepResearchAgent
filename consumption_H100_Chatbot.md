# Report on Energy Consumption of an 8xH100 System for LLM Inference

Based on available information, a system equipped with 8 NVIDIA H100 GPUs, such as the NVIDIA DGX H100, typically consumes a significant amount of power.  The power consumption of the DGX H100 system is reported to be between 6.4 kW and 11.3 kW, with typical usage reaching up to 10 kW [1, 2, 3, 4, 5].  Another source states that a server with 8 NVIDIA H100 GPUs generally draws around 10.2 kW [6]. For the purpose of this calculation, we will use a representative power consumption of 10.2 kW (10200 W).

We are given an inference throughput of 3872 tokens per second for this system. To generate 1 million LLM output tokens, the time required can be calculated as follows:

Time (seconds) = 1,000,000 tokens / 3872 tokens/second ≈ 258.26 seconds

To convert this time to hours, we divide by 3600:

Time (hours) = 258.26 seconds / 3600 seconds/hour ≈ 0.0717 hours

Now, we can calculate the energy consumption in Watt-hours (Wh) using the formula:

Energy (Wh) = Power (W) × Time (hours)

Energy (Wh) = 10200 W × 0.0717 hours ≈ 731.34 Wh

Therefore, an 8xH100 system, consuming approximately 10.2 kW of power and operating at an inference throughput of 3872 tokens/s, is estimated to consume around 731.34 Wh to generate 1 million LLM output tokens.

It's important to note that the actual power consumption can vary based on the specific configuration, workload, and utilization rate of the GPUs and the entire system [7]. The provided value is an estimation based on the typical power draw of such systems and the given throughput.

# References

[1] [server-parts.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUBnsYu48TpjJzUpvUIYH0ys5J4xzvD_q3u-LcKn9cEbrs2QlVzKXSCLAlPc_nRBk2bPXalJz38x10Cq5S4bArOT_u98YHVHf2fCXYAKeF3rOiri1QFNnAXXVQ7LijemLmWdHFoW7Y-ghmtc6c5M7A==)  
[2] [weka.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUBnsYspQ2_r9Sw4_Jc1MliPX1HAYhkL0TyUdOtKmkQCFqxJivhieFlKMHzYosGpuFaHUrNPIRvtmgQVtoBEi6JG4Og9iKO5085cl2GTYm7xgOCNyS3yKDD5m5R03a87x1_nZY418mZMNISXsjW2QKa3JH2sxr0=)  
[3] [hyperstack.cloud](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUBnsYt-gXBhTrdOFHzJH-uakcmxqJZIUSY_RDMkZcYB1BAlZdgYP-m8VbFiSoUcHrVQys3aKpaCt8TV3qTGv72TwgmpS6FmU_qzVHZ_9b3gkSqivJkL9kL0cuR5dodeFc1P19beNzFTXa2sepN3tnInuYEo-o5SK1YyJvY-BRII-ogqUETt-pgf2z0MTHIghKhUhZzfQE6PqoAuw6qLc_pSoJzQbIMFhlLlS1cgUuAAyaRxf28MtnxLmK6K9YwICZJulkGDJdqC)  
[4] [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUBnsYvzAJ32NPghh_6HEX3ZoSy_3ZEf6X-Dgxiv3MeJq84OeeLw_32BMlO2Ubs5qaHUSSdNrbKqDiQRbN2c8HxFxy2JOt1SPGz7haK9cQ4UiEnrIU3lEuX_sbv3krHBsTPkwU2y1mERV5_p7Pw18Fb7LhwVzgv1T4V_o4ff_Y9hj3wCIYaxHMv_I1OuCzIRyfP7_Cvux5g=)  
[5] [trgdatacenters.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUBnsYtluXrxJ6uyMWLZ7OqDWGEkV6mBnMaEOyRn1TCKRZygj4bI0pSP-eweLlzv8gWf6_M_GCClhL4OQip7VTMNG6b4hTRiIKpZkmktWofo5nRaITSWebRKbSMQRP3dSfqqDhllu2iEJWe4iHc8akdVJBfbFHjam7epK2-QYGzk8_d65cc=)  
[6] [semianalysis.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUBnsYt9ipFHxFE0b1TBltTJufkyaLqoFo0yvhFQsARd3b9-Yuy38FyPBZEckgh73H91E_TmPyFeQtlTb2M4_cxtAVEsFO73GM8OTyYco3vEFYHaw4CRI5ONCQAd9VcOWCdbs4jCHPBRlriqarbR9TI_PJiA_D7m_IjSaG2-E7B4bJWmm2I=)  
[7] [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUBnsYvuIHi90sJ5bzwn0JFgNvL5iOVnWGp0HNaC_7MZAKi1n5YmoW5m2QcFT-TxlJbSN5dooe3_dFXbqWqq1wB-5hJl2w5GhI5beqYJQW6DX7YXlz7Mq9UjaUlvShUiqp7Gcoox0ZHAVbsCzFDsCXRpJteUaAJSh4rTtkYo1fTOQ_kR6hp7tcJsLLNJs9A95J7tT7eseqtuw-Y22Piw4wOSYGz3)