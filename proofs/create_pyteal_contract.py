import calculator_pyteal
import call_calculator_pyteal

if __name__ == "__main__":

    approval, clear, _ = calculator_pyteal.compile_to_teal()

    with open("calculator_approval.teal", "w") as f:
        f.write(approval)
    with open("calculator_clear.teal", "w") as f:
        f.write(clear)

    approval, clear, _ = call_calculator_pyteal.compile_to_teal()

    with open("call_calculator_approval.teal", "w") as f:
        f.write(approval)
    with open("call_calculator_clear.teal", "w") as f:
        f.write(clear)
