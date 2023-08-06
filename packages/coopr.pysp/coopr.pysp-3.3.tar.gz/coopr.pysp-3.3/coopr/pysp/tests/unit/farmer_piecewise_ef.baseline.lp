\* Source Pyomo model name=MASTER *\

min 
MASTER:
+1.000000 EXPECTED_COST_RootNode
 +0.0 ONE_VAR_CONSTANT

s.t.

c_e_BelowAverageScenario_DevotedAcreage_CORN_:
-1.000000 BelowAverageScenario_DevotedAcreage(CORN)
+1.000000 RootNode_DevotedAcreage(CORN)
= 0.0

c_e_AverageScenario_DevotedAcreage_CORN_:
-1.000000 AverageScenario_DevotedAcreage(CORN)
+1.000000 RootNode_DevotedAcreage(CORN)
= 0.0

c_e_AboveAverageScenario_DevotedAcreage_CORN_:
-1.000000 AboveAverageScenario_DevotedAcreage(CORN)
+1.000000 RootNode_DevotedAcreage(CORN)
= 0.0

c_e_BelowAverageScenario_DevotedAcreage_SUGAR_BEETS_:
-1.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 RootNode_DevotedAcreage(SUGAR_BEETS)
= 0.0

c_e_AverageScenario_DevotedAcreage_SUGAR_BEETS_:
-1.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 RootNode_DevotedAcreage(SUGAR_BEETS)
= 0.0

c_e_AboveAverageScenario_DevotedAcreage_SUGAR_BEETS_:
-1.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 RootNode_DevotedAcreage(SUGAR_BEETS)
= 0.0

c_e_BelowAverageScenario_DevotedAcreage_WHEAT_:
-1.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
+1.000000 RootNode_DevotedAcreage(WHEAT)
= 0.0

c_e_AverageScenario_DevotedAcreage_WHEAT_:
-1.000000 AverageScenario_DevotedAcreage(WHEAT)
+1.000000 RootNode_DevotedAcreage(WHEAT)
= 0.0

c_e_AboveAverageScenario_DevotedAcreage_WHEAT_:
-1.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
+1.000000 RootNode_DevotedAcreage(WHEAT)
= 0.0

c_e_BelowAverageScenario_RootNode_FirstStageCost_None_:
-1.000000 BelowAverageScenario_FirstStageCost
+1.000000 RootNode_FirstStageCost
= 0.0

c_e_AverageScenario_RootNode_FirstStageCost_None_:
-1.000000 AverageScenario_FirstStageCost
+1.000000 RootNode_FirstStageCost
= 0.0

c_e_AboveAverageScenario_RootNode_FirstStageCost_None_:
-1.000000 AboveAverageScenario_FirstStageCost
+1.000000 RootNode_FirstStageCost
= 0.0

c_e_AboveAverageScenario_AboveAverageNode_SecondStageCost_None_:
+1.000000 AboveAverageNode_SecondStageCost
-1.000000 AboveAverageScenario_SecondStageCost
= 0.0

c_e_BelowAverageScenario_BelowAverageNode_SecondStageCost_None_:
+1.000000 BelowAverageNode_SecondStageCost
-1.000000 BelowAverageScenario_SecondStageCost
= 0.0

c_e_AverageScenario_AverageNode_SecondStageCost_None_:
+1.000000 AverageNode_SecondStageCost
-1.000000 AverageScenario_SecondStageCost
= 0.0

c_e_COST_RootNode_FirstStageCost_None_:
-0.333333 EXPECTED_COST_AboveAverageNode
-0.333333 EXPECTED_COST_AverageNode
-0.333333 EXPECTED_COST_BelowAverageNode
+1.000000 EXPECTED_COST_RootNode
-1.000000 RootNode_FirstStageCost
= 0.0

c_e_COST_AboveAverageNode_SecondStageCost_None_:
-1.000000 AboveAverageNode_SecondStageCost
+1.000000 EXPECTED_COST_AboveAverageNode
= 0.0

c_e_COST_BelowAverageNode_SecondStageCost_None_:
-1.000000 BelowAverageNode_SecondStageCost
+1.000000 EXPECTED_COST_BelowAverageNode
= 0.0

c_e_COST_AverageNode_SecondStageCost_None_:
-1.000000 AverageNode_SecondStageCost
+1.000000 EXPECTED_COST_AverageNode
= 0.0

c_u_AverageScenario_ConstrainTotalAcreage_:
+1.000000 AverageScenario_DevotedAcreage(CORN)
+1.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AverageScenario_DevotedAcreage(WHEAT)
<= 500.0

c_l_AverageScenario_EnforceCattleFeedRequirement(CORN)_:
+3.000000 AverageScenario_DevotedAcreage(CORN)
+1.000000 AverageScenario_QuantityPurchased(CORN)
-1.000000 AverageScenario_QuantitySold(CORN)
>= 240.0

c_l_AverageScenario_EnforceCattleFeedRequirement(SUGAR_BEETS)_:
+20.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AverageScenario_QuantityPurchased(SUGAR_BEETS)
-1.000000 AverageScenario_QuantitySold(SUGAR_BEETS)
>= 0.0

c_l_AverageScenario_EnforceCattleFeedRequirement(WHEAT)_:
+2.500000 AverageScenario_DevotedAcreage(WHEAT)
+1.000000 AverageScenario_QuantityPurchased(WHEAT)
-1.000000 AverageScenario_QuantitySold(WHEAT)
>= 200.0

c_u_AverageScenario_LimitAmountSold(CORN)_:
-3.000000 AverageScenario_DevotedAcreage(CORN)
+1.000000 AverageScenario_QuantitySold(CORN)
<= 0.0

c_u_AverageScenario_LimitAmountSold(SUGAR_BEETS)_:
-20.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AverageScenario_QuantitySold(SUGAR_BEETS)
<= 0.0

c_u_AverageScenario_LimitAmountSold(WHEAT)_:
-2.500000 AverageScenario_DevotedAcreage(WHEAT)
+1.000000 AverageScenario_QuantitySold(WHEAT)
<= 0.0

c_e_AverageScenario_ComputeFirstStageCost_:
-230.000000 AverageScenario_DevotedAcreage(CORN)
-260.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
-150.000000 AverageScenario_DevotedAcreage(WHEAT)
+1.000000 AverageScenario_FirstStageCost
= 0.0

c_e_AverageScenario_ComputeSecondStageCost_:
+1.000000 AverageScenario_Profit(CORN)
+1.000000 AverageScenario_Profit(SUGAR_BEETS)
+1.000000 AverageScenario_Profit(WHEAT)
-210.000000 AverageScenario_QuantityPurchased(CORN)
-100000.000000 AverageScenario_QuantityPurchased(SUGAR_BEETS)
-238.000000 AverageScenario_QuantityPurchased(WHEAT)
+1.000000 AverageScenario_SecondStageCost
= 0.0

c_e_AverageScenario_ComputeProfits(CORN)_SOS2_constraint1_:
-5000.000000 AverageScenario_ComputeProfits(CORN)_SOS2_y(1)
-10000.000000 AverageScenario_ComputeProfits(CORN)_SOS2_y(2)
+1.000000 AverageScenario_QuantitySold(CORN)
= 0.0

c_u_AverageScenario_ComputeProfits(CORN)_SOS2_constraint2_:
-5015000.000000 AverageScenario_ComputeProfits(CORN)_SOS2_y(1)
-20030000.000000 AverageScenario_ComputeProfits(CORN)_SOS2_y(2)
+1.000000 AverageScenario_Profit(CORN)
<= 0.0

c_e_AverageScenario_ComputeProfits(CORN)_SOS2_constraint3_:
+1.000000 AverageScenario_ComputeProfits(CORN)_SOS2_y(0)
+1.000000 AverageScenario_ComputeProfits(CORN)_SOS2_y(1)
+1.000000 AverageScenario_ComputeProfits(CORN)_SOS2_y(2)
= 1.0

c_e_AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint1_:
-5000.000000 AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
-10000.000000 AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
+1.000000 AverageScenario_QuantitySold(SUGAR_BEETS)
= 0.0

c_u_AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint2_:
-1255000.000000 AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
-5010000.000000 AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
+1.000000 AverageScenario_Profit(SUGAR_BEETS)
<= 0.0

c_e_AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint3_:
+1.000000 AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0)
+1.000000 AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
+1.000000 AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
= 1.0

c_e_AverageScenario_ComputeProfits(WHEAT)_SOS2_constraint1_:
-5000.000000 AverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
-10000.000000 AverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
+1.000000 AverageScenario_QuantitySold(WHEAT)
= 0.0

c_u_AverageScenario_ComputeProfits(WHEAT)_SOS2_constraint2_:
-12505000.000000 AverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
-50010000.000000 AverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
+1.000000 AverageScenario_Profit(WHEAT)
<= 0.0

c_e_AverageScenario_ComputeProfits(WHEAT)_SOS2_constraint3_:
+1.000000 AverageScenario_ComputeProfits(WHEAT)_SOS2_y(0)
+1.000000 AverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
+1.000000 AverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
= 1.0

c_u_BelowAverageScenario_ConstrainTotalAcreage_:
+1.000000 BelowAverageScenario_DevotedAcreage(CORN)
+1.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
<= 500.0

c_l_BelowAverageScenario_EnforceCattleFeedRequirement(CORN)_:
+2.400000 BelowAverageScenario_DevotedAcreage(CORN)
+1.000000 BelowAverageScenario_QuantityPurchased(CORN)
-1.000000 BelowAverageScenario_QuantitySold(CORN)
>= 240.0

c_l_BelowAverageScenario_EnforceCattleFeedRequirement(SUGAR_BEETS)_:
+16.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 BelowAverageScenario_QuantityPurchased(SUGAR_BEETS)
-1.000000 BelowAverageScenario_QuantitySold(SUGAR_BEETS)
>= 0.0

c_l_BelowAverageScenario_EnforceCattleFeedRequirement(WHEAT)_:
+2.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
+1.000000 BelowAverageScenario_QuantityPurchased(WHEAT)
-1.000000 BelowAverageScenario_QuantitySold(WHEAT)
>= 200.0

c_u_BelowAverageScenario_LimitAmountSold(CORN)_:
-2.400000 BelowAverageScenario_DevotedAcreage(CORN)
+1.000000 BelowAverageScenario_QuantitySold(CORN)
<= 0.0

c_u_BelowAverageScenario_LimitAmountSold(SUGAR_BEETS)_:
-16.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 BelowAverageScenario_QuantitySold(SUGAR_BEETS)
<= 0.0

c_u_BelowAverageScenario_LimitAmountSold(WHEAT)_:
-2.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
+1.000000 BelowAverageScenario_QuantitySold(WHEAT)
<= 0.0

c_e_BelowAverageScenario_ComputeFirstStageCost_:
-230.000000 BelowAverageScenario_DevotedAcreage(CORN)
-260.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
-150.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
+1.000000 BelowAverageScenario_FirstStageCost
= 0.0

c_e_BelowAverageScenario_ComputeSecondStageCost_:
+1.000000 BelowAverageScenario_Profit(CORN)
+1.000000 BelowAverageScenario_Profit(SUGAR_BEETS)
+1.000000 BelowAverageScenario_Profit(WHEAT)
-210.000000 BelowAverageScenario_QuantityPurchased(CORN)
-100000.000000 BelowAverageScenario_QuantityPurchased(SUGAR_BEETS)
-238.000000 BelowAverageScenario_QuantityPurchased(WHEAT)
+1.000000 BelowAverageScenario_SecondStageCost
= 0.0

c_e_BelowAverageScenario_ComputeProfits(CORN)_SOS2_constraint1_:
-4000.000000 BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(1)
-8000.000000 BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(2)
+1.000000 BelowAverageScenario_QuantitySold(CORN)
= 0.0

c_u_BelowAverageScenario_ComputeProfits(CORN)_SOS2_constraint2_:
-3212000.000000 BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(1)
-12824000.000000 BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(2)
+1.000000 BelowAverageScenario_Profit(CORN)
<= 0.0

c_e_BelowAverageScenario_ComputeProfits(CORN)_SOS2_constraint3_:
+1.000000 BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(0)
+1.000000 BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(1)
+1.000000 BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(2)
= 1.0

c_e_BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint1_:
-4000.000000 BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
-8000.000000 BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
+1.000000 BelowAverageScenario_QuantitySold(SUGAR_BEETS)
= 0.0

c_u_BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint2_:
-804000.000000 BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
-3208000.000000 BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
+1.000000 BelowAverageScenario_Profit(SUGAR_BEETS)
<= 0.0

c_e_BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint3_:
+1.000000 BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0)
+1.000000 BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
+1.000000 BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
= 1.0

c_e_BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_constraint1_:
-4000.000000 BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
-8000.000000 BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
+1.000000 BelowAverageScenario_QuantitySold(WHEAT)
= 0.0

c_u_BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_constraint2_:
-8004000.000000 BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
-32008000.000000 BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
+1.000000 BelowAverageScenario_Profit(WHEAT)
<= 0.0

c_e_BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_constraint3_:
+1.000000 BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(0)
+1.000000 BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
+1.000000 BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
= 1.0

c_u_AboveAverageScenario_ConstrainTotalAcreage_:
+1.000000 AboveAverageScenario_DevotedAcreage(CORN)
+1.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
<= 500.0

c_l_AboveAverageScenario_EnforceCattleFeedRequirement(CORN)_:
+3.600000 AboveAverageScenario_DevotedAcreage(CORN)
+1.000000 AboveAverageScenario_QuantityPurchased(CORN)
-1.000000 AboveAverageScenario_QuantitySold(CORN)
>= 240.0

c_l_AboveAverageScenario_EnforceCattleFeedRequirement(SUGAR_BEETS)_:
+24.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AboveAverageScenario_QuantityPurchased(SUGAR_BEETS)
-1.000000 AboveAverageScenario_QuantitySold(SUGAR_BEETS)
>= 0.0

c_l_AboveAverageScenario_EnforceCattleFeedRequirement(WHEAT)_:
+3.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
+1.000000 AboveAverageScenario_QuantityPurchased(WHEAT)
-1.000000 AboveAverageScenario_QuantitySold(WHEAT)
>= 200.0

c_u_AboveAverageScenario_LimitAmountSold(CORN)_:
-3.600000 AboveAverageScenario_DevotedAcreage(CORN)
+1.000000 AboveAverageScenario_QuantitySold(CORN)
<= 0.0

c_u_AboveAverageScenario_LimitAmountSold(SUGAR_BEETS)_:
-24.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AboveAverageScenario_QuantitySold(SUGAR_BEETS)
<= 0.0

c_u_AboveAverageScenario_LimitAmountSold(WHEAT)_:
-3.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
+1.000000 AboveAverageScenario_QuantitySold(WHEAT)
<= 0.0

c_e_AboveAverageScenario_ComputeFirstStageCost_:
-230.000000 AboveAverageScenario_DevotedAcreage(CORN)
-260.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
-150.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
+1.000000 AboveAverageScenario_FirstStageCost
= 0.0

c_e_AboveAverageScenario_ComputeSecondStageCost_:
+1.000000 AboveAverageScenario_Profit(CORN)
+1.000000 AboveAverageScenario_Profit(SUGAR_BEETS)
+1.000000 AboveAverageScenario_Profit(WHEAT)
-210.000000 AboveAverageScenario_QuantityPurchased(CORN)
-100000.000000 AboveAverageScenario_QuantityPurchased(SUGAR_BEETS)
-238.000000 AboveAverageScenario_QuantityPurchased(WHEAT)
+1.000000 AboveAverageScenario_SecondStageCost
= 0.0

c_e_AboveAverageScenario_ComputeProfits(CORN)_SOS2_constraint1_:
-6000.000000 AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(1)
-12000.000000 AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(2)
+1.000000 AboveAverageScenario_QuantitySold(CORN)
= 0.0

c_u_AboveAverageScenario_ComputeProfits(CORN)_SOS2_constraint2_:
-7218000.000000 AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(1)
-28836000.000000 AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(2)
+1.000000 AboveAverageScenario_Profit(CORN)
<= 0.0

c_e_AboveAverageScenario_ComputeProfits(CORN)_SOS2_constraint3_:
+1.000000 AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(0)
+1.000000 AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(1)
+1.000000 AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(2)
= 1.0

c_e_AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint1_:
-6000.000000 AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
-12000.000000 AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
+1.000000 AboveAverageScenario_QuantitySold(SUGAR_BEETS)
= 0.0

c_u_AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint2_:
-1806000.000000 AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
-7212000.000000 AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
+1.000000 AboveAverageScenario_Profit(SUGAR_BEETS)
<= 0.0

c_e_AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint3_:
+1.000000 AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0)
+1.000000 AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1)
+1.000000 AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2)
= 1.0

c_e_AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_constraint1_:
-6000.000000 AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
-12000.000000 AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
+1.000000 AboveAverageScenario_QuantitySold(WHEAT)
= 0.0

c_u_AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_constraint2_:
-18006000.000000 AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
-72012000.000000 AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
+1.000000 AboveAverageScenario_Profit(WHEAT)
<= 0.0

c_e_AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_constraint3_:
+1.000000 AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(0)
+1.000000 AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1)
+1.000000 AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2)
= 1.0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds 
    -inf <= RootNode_DevotedAcreage(CORN) <= +inf
    -inf <= RootNode_DevotedAcreage(SUGAR_BEETS) <= +inf
    -inf <= RootNode_DevotedAcreage(WHEAT) <= +inf
    -inf <= EXPECTED_COST_RootNode <= +inf
    -inf <= EXPECTED_COST_AboveAverageNode <= +inf
    -inf <= EXPECTED_COST_BelowAverageNode <= +inf
    -inf <= EXPECTED_COST_AverageNode <= +inf
    -inf <= RootNode_FirstStageCost <= +inf
    -inf <= AboveAverageNode_SecondStageCost <= +inf
    -inf <= BelowAverageNode_SecondStageCost <= +inf
    -inf <= AverageNode_SecondStageCost <= +inf
   0.0 <= AverageScenario_DevotedAcreage(CORN) <= 500
   0.0 <= AverageScenario_DevotedAcreage(SUGAR_BEETS) <= 500
   0.0 <= AverageScenario_DevotedAcreage(WHEAT) <= 500
   0.0 <= AverageScenario_QuantityPurchased(CORN) <= +inf
   0.0 <= AverageScenario_QuantityPurchased(SUGAR_BEETS) <= +inf
   0.0 <= AverageScenario_QuantityPurchased(WHEAT) <= +inf
   0.0 <= AverageScenario_QuantitySold(CORN) <= 10000
   0.0 <= AverageScenario_QuantitySold(SUGAR_BEETS) <= 10000
   0.0 <= AverageScenario_QuantitySold(WHEAT) <= 10000
   0 <= AverageScenario_Profit(CORN) <= +inf
   0 <= AverageScenario_Profit(SUGAR_BEETS) <= +inf
   0 <= AverageScenario_Profit(WHEAT) <= +inf
    -inf <= AverageScenario_FirstStageCost <= +inf
    -inf <= AverageScenario_SecondStageCost <= +inf
   0 <= AverageScenario_ComputeProfits(CORN)_SOS2_y(0) <= +inf
   0 <= AverageScenario_ComputeProfits(CORN)_SOS2_y(1) <= +inf
   0 <= AverageScenario_ComputeProfits(CORN)_SOS2_y(2) <= +inf
   0 <= AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0) <= +inf
   0 <= AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1) <= +inf
   0 <= AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2) <= +inf
   0 <= AverageScenario_ComputeProfits(WHEAT)_SOS2_y(0) <= +inf
   0 <= AverageScenario_ComputeProfits(WHEAT)_SOS2_y(1) <= +inf
   0 <= AverageScenario_ComputeProfits(WHEAT)_SOS2_y(2) <= +inf
   0.0 <= BelowAverageScenario_DevotedAcreage(CORN) <= 500
   0.0 <= BelowAverageScenario_DevotedAcreage(SUGAR_BEETS) <= 500
   0.0 <= BelowAverageScenario_DevotedAcreage(WHEAT) <= 500
   0.0 <= BelowAverageScenario_QuantityPurchased(CORN) <= +inf
   0.0 <= BelowAverageScenario_QuantityPurchased(SUGAR_BEETS) <= +inf
   0.0 <= BelowAverageScenario_QuantityPurchased(WHEAT) <= +inf
   0.0 <= BelowAverageScenario_QuantitySold(CORN) <= 8000
   0.0 <= BelowAverageScenario_QuantitySold(SUGAR_BEETS) <= 8000
   0.0 <= BelowAverageScenario_QuantitySold(WHEAT) <= 8000
   0 <= BelowAverageScenario_Profit(CORN) <= +inf
   0 <= BelowAverageScenario_Profit(SUGAR_BEETS) <= +inf
   0 <= BelowAverageScenario_Profit(WHEAT) <= +inf
    -inf <= BelowAverageScenario_FirstStageCost <= +inf
    -inf <= BelowAverageScenario_SecondStageCost <= +inf
   0 <= BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(0) <= +inf
   0 <= BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(1) <= +inf
   0 <= BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(2) <= +inf
   0 <= BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0) <= +inf
   0 <= BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1) <= +inf
   0 <= BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2) <= +inf
   0 <= BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(0) <= +inf
   0 <= BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1) <= +inf
   0 <= BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2) <= +inf
   0.0 <= AboveAverageScenario_DevotedAcreage(CORN) <= 500
   0.0 <= AboveAverageScenario_DevotedAcreage(SUGAR_BEETS) <= 500
   0.0 <= AboveAverageScenario_DevotedAcreage(WHEAT) <= 500
   0.0 <= AboveAverageScenario_QuantityPurchased(CORN) <= +inf
   0.0 <= AboveAverageScenario_QuantityPurchased(SUGAR_BEETS) <= +inf
   0.0 <= AboveAverageScenario_QuantityPurchased(WHEAT) <= +inf
   0.0 <= AboveAverageScenario_QuantitySold(CORN) <= 12000
   0.0 <= AboveAverageScenario_QuantitySold(SUGAR_BEETS) <= 12000
   0.0 <= AboveAverageScenario_QuantitySold(WHEAT) <= 12000
   0 <= AboveAverageScenario_Profit(CORN) <= +inf
   0 <= AboveAverageScenario_Profit(SUGAR_BEETS) <= +inf
   0 <= AboveAverageScenario_Profit(WHEAT) <= +inf
    -inf <= AboveAverageScenario_FirstStageCost <= +inf
    -inf <= AboveAverageScenario_SecondStageCost <= +inf
   0 <= AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(0) <= +inf
   0 <= AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(1) <= +inf
   0 <= AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(2) <= +inf
   0 <= AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0) <= +inf
   0 <= AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1) <= +inf
   0 <= AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2) <= +inf
   0 <= AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(0) <= +inf
   0 <= AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1) <= +inf
   0 <= AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2) <= +inf
SOS
AverageScenario_ComputeProfits(CORN)_SOS2_constraint4_: S2::
AverageScenario_ComputeProfits(CORN)_SOS2_y(0):1.000000
AverageScenario_ComputeProfits(CORN)_SOS2_y(1):2.000000
AverageScenario_ComputeProfits(CORN)_SOS2_y(2):3.000000
AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint4_: S2::
AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0):1.000000
AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1):2.000000
AverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2):3.000000
AverageScenario_ComputeProfits(WHEAT)_SOS2_constraint4_: S2::
AverageScenario_ComputeProfits(WHEAT)_SOS2_y(0):1.000000
AverageScenario_ComputeProfits(WHEAT)_SOS2_y(1):2.000000
AverageScenario_ComputeProfits(WHEAT)_SOS2_y(2):3.000000
BelowAverageScenario_ComputeProfits(CORN)_SOS2_constraint4_: S2::
BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(0):1.000000
BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(1):2.000000
BelowAverageScenario_ComputeProfits(CORN)_SOS2_y(2):3.000000
BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint4_: S2::
BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0):1.000000
BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1):2.000000
BelowAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2):3.000000
BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_constraint4_: S2::
BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(0):1.000000
BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1):2.000000
BelowAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2):3.000000
AboveAverageScenario_ComputeProfits(CORN)_SOS2_constraint4_: S2::
AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(0):1.000000
AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(1):2.000000
AboveAverageScenario_ComputeProfits(CORN)_SOS2_y(2):3.000000
AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_constraint4_: S2::
AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(0):1.000000
AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(1):2.000000
AboveAverageScenario_ComputeProfits(SUGAR_BEETS)_SOS2_y(2):3.000000
AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_constraint4_: S2::
AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(0):1.000000
AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(1):2.000000
AboveAverageScenario_ComputeProfits(WHEAT)_SOS2_y(2):3.000000
end 
